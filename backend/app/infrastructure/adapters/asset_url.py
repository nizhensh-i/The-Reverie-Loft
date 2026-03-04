from ...domain.ports.asset_url import AssetUrlPort
from ...utils.common import get_avatars_url


class AvatarUrlAdapter(AssetUrlPort):
    @staticmethod
    def build(key: str | None) -> str | None:
        return get_avatars_url(key)
