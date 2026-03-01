from enum import Enum, IntEnum


class PermissionCode(IntEnum):
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class PostTypeCode(str, Enum):
    TEXT = "text"
    MARKDOWN = "markdown"


class NotificationTypeCode(str, Enum):
    AT = "at"
    COMMENT = "comment"
    REPLY = "reply"
    LIKE = "like"
    CHAT = "chat"
    NEW_POST = "new_post"


class InterestImageTypeCode(str, Enum):
    MOVIE = "movie"
    BOOK = "book"
