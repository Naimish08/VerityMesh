import tiktoken

def chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> list[dict]:
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    chunks = []
    
    start = 0
    idx = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunk_text = enc.decode(chunk_tokens)
        chunks.append({"content": chunk_text, "chunk_index": idx, "metadata": {"token_count": len(chunk_tokens)}})
        idx += 1
        start += chunk_size - overlap
        
    return chunks
