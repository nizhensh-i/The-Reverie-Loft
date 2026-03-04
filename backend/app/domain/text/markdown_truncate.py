import re


class MarkdownTruncator:
    @staticmethod
    def get_smart_preview(content, is_markdown=True, max_lines=3, max_chars=200):
        if not content:
            return ""

        if not is_markdown:
            content = content.strip()
            return content[:max_chars] + ("..." if len(content) > max_chars else "")

        content = content.lstrip()
        blocks = re.split(r"\n\s*\n", content)
        preview_blocks = blocks[:max_lines]
        preview_text = "\n\n".join(preview_blocks)

        if len(preview_text) > max_chars:
            preview_text = preview_text[:max_chars] + "..."

        if preview_text.count("```") % 2 != 0:
            preview_text += "\n```"

        last_line = preview_text.split("\n")[-1]
        if last_line.count("**") % 2 != 0:
            preview_text += "**"
        elif last_line.count("*") % 2 != 0:
            preview_text += "*"

        return preview_text
