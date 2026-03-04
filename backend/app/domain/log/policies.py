def normalize_log_delete_ids(ids):
    if not ids:
        return []
    return list(dict.fromkeys(ids))
