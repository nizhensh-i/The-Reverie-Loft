from ...domain.ports.oauth import OAuthNetworkPort
from ..oauth import has_oauth_network_error_message


class OAuthNetworkAdapter(OAuthNetworkPort):
    @staticmethod
    def has_network_error_message(message: str) -> bool:
        return has_oauth_network_error_message(message)
