from ...domain.ports.settings import PaginationSettingsPort


class FlaskConfigSettingsAdapter(PaginationSettingsPort):
    def __init__(self, config):
        self._config = config

    def posts_per_page(self) -> int:
        return int(self._config.get("FLASKY_POSTS_PER_PAGE", 20))

    def followers_per_page(self) -> int:
        return int(self._config.get("FLASKY_FOLLOWERS_PER_PAGE", 20))

    def chat_per_page(self) -> int:
        return int(self._config.get("FLASKY_CHAT_PER_PAGE", 20))
