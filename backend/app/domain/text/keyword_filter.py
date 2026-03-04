import os


class DFAFilter:
    def __init__(self):
        self.keyword_chains = {}
        self.delimit = "\x00"
        current_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(current_dir, "keywords")
        self.parse(full_path)

    def add(self, keyword):
        keyword = keyword.lower()
        chars = keyword.strip()
        if not chars:
            return

        level = self.keyword_chains
        for idx in range(len(chars)):
            if chars[idx] in level:
                level = level[chars[idx]]
            else:
                if not isinstance(level, dict):
                    break
                for jdx in range(idx, len(chars)):
                    level[chars[jdx]] = {}
                    last_level, last_char = level, chars[jdx]
                    level = level[chars[jdx]]
                last_level[last_char] = {self.delimit: 0}
                break

        if idx == len(chars) - 1:
            level[self.delimit] = 0

    def parse(self, path):
        with open(path, encoding="utf-8") as handle:
            for keyword in handle:
                self.add(keyword.strip())

    def filter(self, message, repl="*"):
        message = (message or "").lower()
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        ret.append(repl * step_ins)
                        start += step_ins - 1
                        break
                else:
                    ret.append(message[start])
                    break
            else:
                ret.append(message[start])
            start += 1

        return "".join(ret)
