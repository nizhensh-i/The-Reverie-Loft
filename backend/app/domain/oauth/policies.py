from urllib.parse import parse_qs, urlencode, urlparse

from ..common.exceptions import ValidationError


def sanitize_oauth_authorize_url(auth_url: str):
    parsed = urlparse(auth_url)
    query_params = parse_qs(parsed.query, keep_blank_values=True)
    encoded_query = urlencode(query_params, doseq=True)
    return parsed._replace(query=encoded_query).geturl()


def parse_bind_state_token(state: str):
    if state.startswith("bind:"):
        return state[5:]
    return None


def ensure_oauth_user_uuid(uuid_value):
    if not uuid_value:
        raise ValidationError("第三方登录缺少 uuid")


def ensure_provider_enabled(*, provider: str, enabled_providers):
    if provider not in enabled_providers:
        raise ValidationError(f"不支持的平台: {provider}")
