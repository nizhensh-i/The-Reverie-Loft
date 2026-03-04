def _normalize_tag_set(values):
    return {str(v).strip() for v in (values or []) if str(v).strip()}


def normalize_tag_changes(*, tag_add, tag_remove):
    add_set = _normalize_tag_set(tag_add)
    remove_set = _normalize_tag_set(tag_remove)
    overlap = add_set & remove_set
    if overlap:
        add_set -= overlap
        remove_set -= overlap
    return add_set, remove_set
