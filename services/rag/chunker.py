def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """把文本切分为若干块：优先按段落，单段超长时做滑动窗口硬切。"""
    text = text.replace("\r\n", "\n").strip()
    if not text:
        return []

    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks = []
    buffer = ""

    for para in paragraphs:
        if len(para) <= chunk_size:
            if buffer and len(buffer) + len(para) + 1 > chunk_size:
                chunks.append(buffer)
                buffer = para
            else:
                buffer = f"{buffer}\n{para}".strip() if buffer else para
        else:
            if buffer:
                chunks.append(buffer)
                buffer = ""
            chunks.extend(_slice(para, chunk_size, overlap))

    if buffer:
        chunks.append(buffer)
    return chunks


def _slice(text: str, chunk_size: int, overlap: int) -> list:
    parts = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        parts.append(text[start:end])
        if end >= n:
            break
        start = end - overlap
    return parts
