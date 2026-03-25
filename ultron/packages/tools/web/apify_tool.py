import os
import httpx
import asyncio

from packages.tools.base_tool import BaseTool
from packages.tools.schemas.apify_schema import ApifyInput, ApifyOutput

class ApifyTool(BaseTool):
    """Invokes Apify actors and retrieves results."""
    input_schema = ApifyInput
    output_schema = ApifyOutput

    def __init__(self):
        super().__init__(
            name="run_apify_actor",
            description="Runs an Apify actor and polls for completion to get results.",
            permission_level="ENTROPY_CHECKED"
        )
        self.api_key = os.getenv("APIFY_KEY")
        self.base_url = "https://api.apify.com/v2"

    async def execute(self, params: ApifyInput) -> ApifyOutput:
        if not self.api_key:
            return ApifyOutput(results=[{"error": "APIFY_KEY missing, simulated mock result for actor", "actor": params.actor_id}])

        run_url = f"{self.base_url}/acts/{params.actor_id}/runs?token={self.api_key}"
        
        async with httpx.AsyncClient() as client:
            # Start run
            response = await client.post(run_url, json=params.run_input)
            response.raise_for_status()
            run_data = response.json().get("data", {})
            run_id = run_data.get("id")
            default_dataset_id = run_data.get("defaultDatasetId")
            
            # Poll for completion
            status_url = f"{self.base_url}/actor-runs/{run_id}?token={self.api_key}"
            while True:
                status_res = await client.get(status_url)
                status_res.raise_for_status()
                current_status = status_res.json().get("data", {}).get("status")
                
                if current_status in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
                    break
                
                await asyncio.sleep(5)
                
            if current_status != "SUCCEEDED":
                raise Exception(f"Apify run failed with status: {current_status}")
                
            # Fetch results
            dataset_url = f"{self.base_url}/datasets/{default_dataset_id}/items?token={self.api_key}"
            dataset_res = await client.get(dataset_url)
            dataset_res.raise_for_status()
            
            results = dataset_res.json()
            return ApifyOutput(results=results)
