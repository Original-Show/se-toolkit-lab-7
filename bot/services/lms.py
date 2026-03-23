import httpx
from config import settings

class LMSError(Exception):
    pass

class LMSClient:
    def __init__(self):
        self.base_url = settings.lms_api_base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {settings.lms_api_key}"}

    async def _get(self, endpoint: str, params: dict = None) -> dict | list:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}{endpoint}", 
                    headers=self.headers, 
                    params=params,
                    timeout=5.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise LMSError(f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down.")
            except httpx.RequestError as e:
                host = self.base_url.replace("http://", "").replace("https://", "")
                raise LMSError(f"connection refused ({host}). Check that the services are running.")

    async def get_health(self) -> str:
        try:
            items = await self._get("/items/")
            count = len(items) if isinstance(items, list) else 0
            return f"Backend is healthy. {count} items available."
        except LMSError as e:
            return f"Backend error: {str(e)}"

    async def get_labs(self) -> str:
        try:
            items = await self._get("/items/")
            if not isinstance(items, list):
                return "Backend returned invalid data."
            
            labs = [item.get("title") for item in items if item.get("type") == "lab"]
            if not labs:
                return "Available labs: None found."
            
            res = "Available labs:\n"
            for lab in sorted(labs):
                res += f"- {lab}\n"
            return res.strip()
        except LMSError as e:
            return f"Backend error: {str(e)}"

    async def get_scores(self, lab_id: str) -> str:
        try:
            data = await self._get("/analytics/pass-rates", params={"lab": lab_id})
            if not data:
                return f"No score data found for {lab_id}."

            res = f"Pass rates for {lab_id}:\n"
            for task in data:
                name = task.get("task", "Unknown Task")
                rate = task.get("avg_score", 0.0)
                attempts = task.get("attempts", 0)
                res += f"- {name}: {rate:.1f}% ({attempts} attempts)\n"
            return res.strip()
        except LMSError as e:
            return f"Backend error: {str(e)}"

    # --- Tool methods for LLM ---
    async def get_items_raw(self): return await self._get("/items/")
    async def get_learners_raw(self): return await self._get("/learners/")
    async def get_scores_raw(self, lab: str): return await self._get("/analytics/scores", {"lab": lab})
    async def get_pass_rates_raw(self, lab: str): return await self._get("/analytics/pass-rates", {"lab": lab})
    async def get_timeline_raw(self, lab: str): return await self._get("/analytics/timeline", {"lab": lab})
    async def get_groups_raw(self, lab: str): return await self._get("/analytics/groups", {"lab": lab})
    async def get_top_learners_raw(self, lab: str, limit: int = 10): return await self._get("/analytics/top-learners", {"lab": lab, "limit": limit})
    async def get_completion_rate_raw(self, lab: str): return await self._get("/analytics/completion-rate", {"lab": lab})
    async def trigger_sync_raw(self):
        async with httpx.AsyncClient() as client:
            try:
                r = await client.post(f"{self.base_url}/pipeline/sync", headers=self.headers, json={}, timeout=10.0)
                r.raise_for_status()
                return r.json()
            except Exception as e:
                return {"error": str(e)}

lms_client = LMSClient()
