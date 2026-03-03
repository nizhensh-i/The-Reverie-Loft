from .asset_url import AvatarUrlAdapter
from .auth import CeleryMailSender, RedisEmailCodeAdapter
from .cache import FlaskCacheAdapter
from .jwt import FlaskJwtAdapter
from .notifications import CeleryNotificationDispatcher
from .oauth import OAuthNetworkAdapter
from .presence import RedisPresenceAdapter
from .settings import FlaskConfigSettingsAdapter
from .storage import QiniuAvatarProvider, QiniuStorageAdapter

__all__ = [
    "CeleryNotificationDispatcher",
    "RedisEmailCodeAdapter",
    "CeleryMailSender",
    "FlaskCacheAdapter",
    "FlaskJwtAdapter",
    "QiniuAvatarProvider",
    "QiniuStorageAdapter",
    "AvatarUrlAdapter",
    "RedisPresenceAdapter",
    "OAuthNetworkAdapter",
    "FlaskConfigSettingsAdapter",
]
