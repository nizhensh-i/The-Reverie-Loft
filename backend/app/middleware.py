from werkzeug.middleware.proxy_fix import ProxyFix


def setup_proxyfix_middleware(app):
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,  # 对应 X-Forwarded-For（信任1层代理）
        x_proto=1,  # 对应 X-Forwarded-Proto（信任1层代理）
        x_host=1,  # 对应 X-Forwarded-Host（信任1层代理）
        x_prefix=1,  # 对应 X-Forwarded-Prefix（信任1层代理）
    )
