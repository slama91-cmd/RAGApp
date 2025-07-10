from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import APIKeyHeader
import faiss
import numpy as np
import pickle
import os

app = FastAPI()
dimension = 1024  # mistral-embed dimension
index = faiss.IndexFlatL2(dimension)
chunk_map = {}  # Maps index ID to chunk text
index_file = "faiss_index.bin"
chunk_map_file = "chunk_map.pkl"
api_key_header = APIKeyHeader(name="X-API-Key")

# Load index if exists
if os.path.exists(index_file):
    index = faiss.read_index(index_file)
    with open(chunk_map_file, "rb") as f:
        chunk_map = pickle.load(f)

@app.post("/add_vectors")
async def add_vectors(vectors: list[list[float]], chunks: list[str]):
    try:
        vectors_np = np.array(vectors, dtype=np.float32)
        if vectors_np.shape[1] != dimension:
            raise ValueError("Invalid vector dimension")
        ids = np.arange(index.ntotal, index.ntotal + len(vectors))
        index.add(vectors_np)
        for i, chunk in zip(ids, chunks):
            chunk_map[i] = chunk
        # Save index and chunk map
        faiss.write_index(index, index_file)
        with open(chunk_map_file, "wb") as f:
            pickle.dump(chunk_map, f)
        return {"status": "success", "added": len(vectors)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import logging
logging.basicConfig(level=logging.DEBUG)
@app.post("/search")
async def search(query_vector: list[float], k: int = 5):
    logging.debug(f"Received query_vector: length={len(query_vector)}, sample={query_vector[:5]}")
    try:
        query_np = np.array([query_vector], dtype=np.float32)
        if query_np.shape[1] != dimension:
            raise ValueError("Invalid query dimension")
        distances, indices = index.search(query_np, k)
        results = [
            {"chunk": chunk_map.get(idx, "Unknown"), "distance": float(dist)}
            for idx, dist in zip(indices[0], distances[0])
        ]
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/index_stats")
async def index_stats(api_key: str = Depends(api_key_header)):
    if api_key != os.getenv("FAISS_API_KEY", "1234a"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return {"total_vectors": index.ntotal, "dimension": dimension}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
