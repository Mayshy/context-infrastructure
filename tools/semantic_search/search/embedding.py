import os
import requests
from typing import List


class EmbeddingClient:
    def __init__(
        self,
        base_url: str = "https://aigc.sankuai.com/v1/openai/native",
        model: str = "text-embedding-miffy-002",
        api_key: str = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key or os.getenv("FRIDAY_APP_ID") or "placeholder"

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def embed(self, text: str) -> List[float]:
        text = text.replace("\n", " ")
        resp = requests.post(
            f"{self.base_url}/embeddings",
            headers=self._headers(),
            json={"input": text, "model": self.model},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["data"][0]["embedding"]

    def embed_batch(self, texts: List[str], batch_size: int = 4) -> List[List[float]]:
        import time
        results = []
        for i in range(0, len(texts), batch_size):
            batch = [t.replace("\n", " ")[:1000].strip() or "." for t in texts[i:i + batch_size]]
            for attempt in range(5):
                resp = requests.post(
                    f"{self.base_url}/embeddings",
                    headers=self._headers(),
                    json={"input": batch, "model": self.model},
                    timeout=30,
                )
                if resp.status_code == 429:
                    time.sleep(2 ** attempt)
                    continue
                resp.raise_for_status()
                break
            body = resp.json()
            data = body.get("data") if body else None
            if not data:
                raise RuntimeError(f"Embedding API returned no data: {body}")
            data.sort(key=lambda x: x["index"])
            results.extend([d["embedding"] for d in data])
        return results
