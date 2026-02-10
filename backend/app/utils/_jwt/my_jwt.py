from flask_jwt_extended import create_access_token, create_refresh_token


class JwtUtils:
    def __init__():
        pass

    def generate_access_token(user_entity):
        """生成访问令牌"""
        return "Bearer " + create_access_token(identity=user_entity)

    def generate_refresh_token(user_entity):
        """生产刷新令牌"""
        return "Bearer " + create_refresh_token(identity=user_entity)

    def revoke_token(token, jwt_redis_blocklist, expire_time):
        """撤销令牌"""
        try:
            jti = token["jti"]
            jwt_redis_blocklist.set(jti, "", ex=expire_time)
            return True
        except Exception as e:
            return False

    def check_freshness(token):
        """检测当前令牌是否为新鲜令牌"""
        if token.get("fresh", False):
            return True
        return False
