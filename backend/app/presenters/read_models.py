import re


def replace_markdown_image_refs(content, pos, image_urls):
    pos2url = {str(_pos): _url for _pos, _url in zip(pos, image_urls)}

    def replacer(match):
        alt = match.group(1)
        position = match.group(2)
        url = pos2url.get(position)
        if url:
            return f"![{alt}]({url})"
        return match.group(0)

    pattern = re.compile(r"!\[([^\]]*)\]\((\d+)\)")
    return pattern.sub(replacer, content)
