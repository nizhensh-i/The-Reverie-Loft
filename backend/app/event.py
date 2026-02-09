# -*- coding: utf-8 -*-
import atexit
import logging
import signal
import sys

import eventlet
from flask import request
from flask_jwt_extended import decode_token
from flask_socketio import ConnectionRefusedError, join_room

from . import db, redis
from .models import Message, Notification, NotificationType, User
from .mycelery.notification_task import create_chat_notifications
from .websocket import init_ws_services

connection, presence, conversation, cleanup = init_ws_services(redis)


def register_cleanup_handlers(app):
    """注册 WebSocket 优雅停机处理器"""

    def shutdown_handler(signum=None, frame=None):
        """优雅停机处理器"""
        if signum:
            signal_name = {signal.SIGTERM: "SIGTERM", signal.SIGINT: "SIGINT"}.get(
                signum, "未知"
            )
            logging.warning(f"接收到终止信号 {signal_name}，正在优雅停机...")
        else:
            logging.warning("应用正常退出，正在清理资源...")

        # 停止清理服务
        cleanup.stop()

        # 可选：清理所有 WebSocket 相关数据
        cleanup.cleanup_all()

        # 确保触发 atexit
        if signum:
            sys.exit(0)

    # 覆盖正常退出
    atexit.register(shutdown_handler)

    # kill <pid> 或 docker stop
    signal.signal(signal.SIGTERM, shutdown_handler)
    # Ctrl+C 中断
    signal.signal(signal.SIGINT, shutdown_handler)

    logging.info("WebSocket 优雅停机处理器已注册")


# 封装为注册函数
def register_ws_events(socketio, app):
    """注册WS事件，绑定传入的socketio实例和app上下文"""

    def verify_token_in_websocket():
        """连接websocket时验证用户身份"""
        try:
            access_token = request.args.get("access_token")
            if not access_token:
                logging.warning("WebSocket连接缺少token")
                raise ConnectionRefusedError("未授权：缺少token")

            raw_token = access_token.replace("Bearer ", "", 1)
            decoded_token = decode_token(raw_token)
            user_id = decoded_token["sub"]
            logging.info(f"WebSocket连接token验证成功，用户ID: {user_id}")
        except Exception as e:
            logging.error(f"WebSocket身份验证失败: {str(e)}", exc_info=True)
            raise ConnectionRefusedError("WebSocket身份验证失败，token解析错误")

        # 检查用户是否存在（DB操作，后续异步场景需绑定上下文）
        user = User.query.get(user_id)
        if not user:
            logging.warning(f"WebSocket连接失败: 用户ID {user_id} 不存在")
            raise ConnectionRefusedError("WebSocket身份验证失败，用户不存在")

        return user.username, user.id

    # 连接事件
    @socketio.on("connect")
    def handle_connect(auth):
        username, user_id = verify_token_in_websocket()

        # 检查是否已有连接，限制单个用户连接数（防止资源滥用）
        existing_sockets = connection.get_bound_sockets(user_id)
        MAX_SOCKETS_PER_USER = 10
        if len(existing_sockets) >= MAX_SOCKETS_PER_USER:
            logging.warning(f"用户 {username} 连接数超过限制 ({MAX_SOCKETS_PER_USER})")
            raise ConnectionRefusedError(f"连接数超过限制，当前连接数: {len(existing_sockets)}")

        # 内存操作同步执行（无阻塞）
        connection.bind_socket_to_user(user_id, request.sid)
        presence.mark_user_online(user_id)
        join_room(str(user_id))

        socket_count = len(connection.get_bound_sockets(user_id))
        logging.info(f"用户 {username} 已连接，新连接ID：{request.sid}，当前总连接数：{socket_count}")

    # 断开事件：纯内存操作，同步执行
    @socketio.on("disconnect")
    def handle_disconnect():
        sid = request.sid
        user_id = connection.unbind_socket(sid)

        if not user_id:
            logging.warning(f"断开连接: 未找到 socket {sid} 对应的用户")
            return

        # 如果该用户已经没有任何 socket → 离线
        remaining_sockets = connection.get_bound_sockets(user_id)
        if not remaining_sockets:
            presence.mark_user_offline(user_id)
            logging.info(f"用户 ID:{user_id} 已完全离线")
        else:
            logging.info(f"用户 ID:{user_id} 断开一个连接，剩余 {len(remaining_sockets)} 个连接")

    # 心跳事件：纯内存操作，同步执行
    @socketio.on("heartbeat")
    def handle_heartbeat():
        username, user_id = verify_token_in_websocket()
        presence.update_last_active(user_id)

        # 记录统计信息（可选，用于监控）
        socket_count = len(connection.get_bound_sockets(user_id))
        logging.debug(f"用户 {username} 发送心跳包，当前连接数: {socket_count}")

    # 进入聊天事件-异步DB操作（标记已读）
    def async_enter_chat(user_id, target_id):
        """异步处理进入聊天的DB操作（标记已读）"""
        with app.app_context():  # 绑定WS应用上下文
            try:
                # 标记消息已读
                updated_messages = Message.query.filter(
                    Message.receiver_id == user_id,
                    Message.sender_id == target_id,
                    Message.is_read.is_(False),
                ).update({"is_read": True}, synchronize_session="fetch")
                logging.info(f"已将 {updated_messages} 条消息标记为已读")

                # 标记通知已读
                updated_notifications = (
                    Notification.query.filter_by(
                        receiver_id=user_id,
                        trigger_user_id=target_id,
                        type=NotificationType.CHAT,
                    )
                    .filter(Notification.is_read.is_(False))
                    .update({"is_read": True})
                )
                logging.info(f"已将 {updated_notifications} 条通知标记为已读")

                db.session.commit()
            except Exception as e:
                db.session.rollback()  # 事务回滚
                logging.error(f"更新消息和通知状态失败: {str(e)}", exc_info=True)

    @socketio.on("enter_chat")
    def handle_enter_chat(data):
        username, user_id = verify_token_in_websocket()
        target_id = data["targetId"]

        # 内存操作同步执行
        conversation.set_active_chat(user_id, target_id)
        presence.update_last_active(user_id)

        logging.info(f"用户 {username} 进入与用户 {target_id} 的聊天页面")

        # DB操作异步执行
        eventlet.spawn_n(async_enter_chat, user_id, target_id)

    # 输入状态事件
    @socketio.on("chat:typing")
    def handle_typing(data):
        """处理用户正在输入事件"""
        username, user_id = verify_token_in_websocket()
        target_id = data.get("target_id")

        if target_id:
            # 标记用户正在输入
            conversation.mark_typing(user_id, target_id)
            logging.info(f"用户 {username} 正在给用户 {target_id} 输入")

            # 向目标用户发送typing事件
            socketio.emit(
                "chat:typing",
                {"sender_id": user_id, "sender_name": username},
                room=str(target_id),
            )

    # 发送消息事件-异步DB操作（消息入库+通知）
    def async_send_message(sender_id, receiver_id, content, sid):
        """异步处理发送消息的DB操作"""
        with app.app_context():
            msg = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
            db.session.add(msg)
            db.session.flush()

            try:
                # 使用正确的在线检测（会检查心跳超时）
                is_online = presence.is_user_online(receiver_id)
                active_chat = conversation.get_active_chat(receiver_id)

                logging.info(
                    f"接收者 {receiver_id} 在线状态: {is_online}, " f"活跃聊天: {active_chat}"
                )

                if is_online and active_chat == sender_id:
                    logging.info(f"用户 {receiver_id} 当前正在与发送者 {sender_id} 聊天")
                    msg.is_read = True
                    socketio.emit("new_message", msg.to_json(), to=str(receiver_id))
                else:
                    # 异步生成通知（Celery任务）
                    create_chat_notifications.delay(receiver_id, sender_id, msg.id)
                    if is_online:
                        logging.info(f"用户 {receiver_id} 在线但不在聊天页面，消息已保存")
                    else:
                        logging.info(f"用户 {receiver_id} 离线，消息已保存")

                db.session.commit()
                socketio.emit("message_sent", msg.to_json(), room=sid)
                logging.info(f"消息 ID:{msg.id} 发送成功")
            except Exception as e:
                db.session.rollback()  # 事务回滚
                logging.error(f"消息发送失败: {str(e)}", exc_info=True)

    @socketio.on("send_message")
    def handle_send_message(data):
        username, sender_id = verify_token_in_websocket()
        receiver_id = data["receiver_id"]
        content = data["content"]
        logging.info(f"用户 {username} 发送消息给用户 {receiver_id}: {content[:20]}...")

        # DB操作异步执行
        eventlet.spawn_n(
            async_send_message, sender_id, receiver_id, content, request.sid
        )
