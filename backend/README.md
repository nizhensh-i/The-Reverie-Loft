# 后端架构说明

后端采用 Clean Architecture 风格分层，并通过依赖注入保持边界清晰。

## 分层与调用关系

简化调用链：

Controller (API/Auth) -> Service -> Domain -> Infrastructure

规则约定：

- Controller 仅做请求/响应编排，不承载业务规则。
- Service 编排用例与业务流程。
- Domain 保持框架无关，定义实体、策略与端口接口。
- Infrastructure 提供 DB/Redis/OAuth/Mail/Storage 等适配器实现。

## 依赖注入（DI）

容器定义在 `app/container.py`，并在 `app/__init__.py` 中完成装配与注入。

关键点：

- 端口定义：`app/domain/ports`
- 适配器实现：`app/infrastructure/adapters`
- Service 依赖端口而非具体实现
- Container 在启动时完成依赖绑定

## 入口与导航

- HTTP 入口：`flasky.py`
- Socket.IO 入口：`flasky_socketio.py`
- 容器装配：`app/container.py`

## 推荐阅读路径

- `app/container.py`
- `app/domain/ports`
- `app/infrastructure/adapters`
- `app/services`
