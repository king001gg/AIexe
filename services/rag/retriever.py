import math
import re
from collections import Counter, defaultdict

_CJK_RE = re.compile(r"[一-鿿]+")
_WORD_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list:
    """中文友好的轻量分词：英文/数字按单词，中文按字符 unigram + bigram。"""
    text = text.lower()
    tokens = []
    tokens.extend(_WORD_RE.findall(text))
    for run in _CJK_RE.findall(text):
        tokens.extend(run)  # unigram
        if len(run) > 1:  # bigram
            tokens.extend(run[i:i + 2] for i in range(len(run) - 1))
    return tokens


class BM25Index:
    """纯 Python BM25 检索索引（无向量库/嵌入模型依赖）。"""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.docs = []
        self.doc_len = []
        self.df = defaultdict(int)
        self.avgdl = 0.0

    def add(self, doc_id: str, title: str, content: str) -> None:
        tf = Counter(tokenize(content))
        self.docs.append({"id": doc_id, "title": title, "content": content, "tf": tf})
        self.doc_len.append(sum(tf.values()))
        for term in tf:
            self.df[term] += 1
        self._update_avgdl()

    def _update_avgdl(self) -> None:
        self.avgdl = sum(self.doc_len) / len(self.doc_len) if self.doc_len else 0.0

    def search(self, query: str, top_k: int = 3) -> list:
        q_terms = set(tokenize(query))
        if not q_terms or not self.docs:
            return []

        n = len(self.docs)
        scored = []
        for idx, doc in enumerate(self.docs):
            dl = self.doc_len[idx]
            score = 0.0
            for term in q_terms:
                tf = doc["tf"].get(term, 0)
                if tf == 0:
                    continue
                df = self.df.get(term, 0)
                idf = math.log((n - df + 0.5) / (df + 0.5) + 1)
                denom = tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
                score += idf * (tf * (self.k1 + 1)) / denom
            if score > 0:
                scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {"id": doc["id"], "title": doc["title"], "content": doc["content"], "score": round(score, 4)}
            for score, doc in scored[:top_k]
        ]
