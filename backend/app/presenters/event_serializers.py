from .api_assembler import map_message, map_notification


def serialize_message_event(message):
    return map_message(message)


def serialize_notification_event(notification):
    return map_notification(notification)


def serialize_notification_events(notifications):
    return [serialize_notification_event(item) for item in notifications]
