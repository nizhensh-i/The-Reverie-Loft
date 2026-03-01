def normalize_message_ids(ids):
    if not ids:
        return []
    return list(dict.fromkeys(ids))


def build_conversation_message_items(messages, *, serializer):
    result = []
    index = len(messages)
    for message in messages:
        item = serializer(message)
        item.update({"id": index})
        result.append(item)
        index -= 1
    return result
