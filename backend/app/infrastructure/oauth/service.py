import os
from dataclasses import dataclass
from typing import Dict, Optional

from flask import url_for
from senweaver_oauth import AuthConfig
from senweaver_oauth.builder import AuthRequestBuilder
from senweaver_oauth.cache import DefaultCacheStore, RedisCacheStore

from ..capabilities import capability_enabled, get_capability, set_capability

APP_NAMES = ["qq", "weibo", "github", "google"]


@dataclass(frozen=True)
class OAuthNetworkErrors:
    timeout_signatures = (
        "timed out",
        "max retries exceeded",
    )
    connection_signatures = (
        "connection to",
        "network unreachable",
    )


def read_oauth_configs(app_names: list[str] | None = None) -> Dict[str, Dict]:
    names = app_names or APP_NAMES
    result = {}
    for name in names:
        prefix = name.upper()
        result[name] = {
            "display_name": name,
            "client_id": os.getenv(f"{prefix}_CLIENT_ID", ""),
            "client_secret": os.getenv(f"{prefix}_CLIENT_SECRET", ""),
            "redirect_uri": os.getenv(f"{prefix}_REDIRECT_URI"),
        }
    return result


def get_frontend_oauth_redirect() -> str:
    host = os.getenv("FLASK_RUN_HOST")
    redirect = f"http://{host}:5172/oauth/callback"
    if os.getenv("FLASK_CONFIG") == "docker":
        redirect = "https://191718.com/oauth/callback"
    return redirect


def detect_oauth_capability(oauth_configs: Optional[Dict[str, Dict]] = None) -> dict:
    configs = oauth_configs or read_oauth_configs()
    if not capability_enabled("redis", default=True):
        reason = (get_capability("redis") or {}).get("reason", "redis unavailable")
        result = {
            "enabled": False,
            "degraded": True,
            "reason": f"disabled because redis unavailable: {reason}",
        }
        set_capability("oauth", **result)
        return result

    providers = [
        name
        for name, cfg in configs.items()
        if cfg.get("client_id") and cfg.get("client_secret")
    ]
    if providers:
        result = {
            "enabled": True,
            "degraded": False,
            "reason": f"enabled providers: {','.join(providers)}",
        }
    else:
        result = {
            "enabled": False,
            "degraded": True,
            "reason": "no oauth providers configured",
        }
    set_capability("oauth", **result)
    return result


def setup_oauth():
    return detect_oauth_capability()


class OAuthInfraService:
    def __init__(self, redis_client, oauth_configs: Optional[Dict[str, Dict]] = None):
        self.redis_client = redis_client
        self.oauth_configs = oauth_configs or read_oauth_configs()
        self._oauth_redis_cache = None

    def enabled_providers(self) -> list[str]:
        detect_oauth_capability(self.oauth_configs)
        return [
            name
            for name, cfg in self.oauth_configs.items()
            if cfg.get("client_id") and cfg.get("client_secret")
        ]

    def _get_oauth_cache_store(self) -> RedisCacheStore:
        if self._oauth_redis_cache is None:
            if self.redis_client is None:
                raise RuntimeError("Redis 客户端未初始化，请确保 flask_redis 已正确配置")

            self._oauth_redis_cache = RedisCacheStore(
                redis_client=self.redis_client,
                prefix="oauth:state:",
                ttl=300,
            )
            DefaultCacheStore.set_instance(self._oauth_redis_cache)
        return self._oauth_redis_cache

    def get_auth_request(self, provider: str):
        config = self.oauth_configs.get(provider)
        if not config:
            raise ValueError(f"未支持的平台: {provider}")
        if not config.get("client_id") or not config.get("client_secret"):
            raise ValueError(f"平台 {provider} 未正确配置")

        redirect_uri = config.get("redirect_uri") or url_for(
            "auth.oauth_callback", provider=provider, _external=True
        )
        if os.getenv("FLASK_CONFIG") == "docker":
            redirect_uri = redirect_uri.replace("auth", "api/auth", 1)

        auth_config = AuthConfig(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            redirect_uri=redirect_uri,
            extras=config.get("extras", {}),
        )
        source_name = config.get("source") or provider

        self._get_oauth_cache_store()

        auth_request = (
            AuthRequestBuilder.builder()
            .source(source_name)
            .auth_config(auth_config)
            .build()
        )
        return auth_request, {"redirect_uri": redirect_uri}


def has_oauth_network_error_message(message: str) -> bool:
    if not message:
        return False

    lowered = message.lower()
    return any(sig in lowered for sig in OAuthNetworkErrors.timeout_signatures) or any(
        sig in lowered for sig in OAuthNetworkErrors.connection_signatures
    )
