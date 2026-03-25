import httpx
from bs4 import BeautifulSoup
from packages.infrastructure.redis_client import UltronRedis

from packages.tools.base_tool import BaseTool
from packages.tools.schemas.nist_schema import NISTInput, NISTOutput

class NISTChemistryTool(BaseTool):
    """Fetches thermochemical data from NIST WebBook."""
    input_schema = NISTInput
    output_schema = NISTOutput

    def __init__(self, redis: UltronRedis):
        super().__init__(
            name="get_nist_data",
            description="Fetches thermochemical data from NIST WebBook and caches in Redis.",
            permission_level="ALWAYS_ALLOWED"
        )
        self.redis = redis
        self.base_url = "https://webbook.nist.gov/cgi/cbook.cgi"

    async def execute(self, params: NISTInput) -> NISTOutput:
        cache_key = f"nist_cache:{params.compound}:{params.temperature_k}:{params.pressure_pa}"
        cached = await self.redis.get(cache_key)
        if cached:
            try:
                import json
                data = json.loads(cached)
                return NISTOutput(**data)
            except Exception:
                pass

        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params={"Name": params.compound, "Units": "SI"})
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            cp, h, s, g = None, None, None, None
            
            # Real parsing: looking for specific rows in tables
            for tr in soup.find_all('tr'):
                th = tr.find('th')
                if not th: continue
                th_text = th.get_text()
                
                tds = tr.find_all('td')
                if not tds: continue
                
                # Usually the first td is the value like "-285.8 ± 0.1"
                val_text = tds[0].get_text(strip=True).split('±')[0].strip()
                try:
                    val = float(val_text)
                    if 'fH°' in th_text or 'Enthalpy of formation' in th_text:
                        if h is None: h = val
                    elif 'S°' in th_text or 'Entropy' in th_text:
                        if s is None: s = val
                    elif 'Cp' in th_text or 'Heat capacity' in th_text:
                        if cp is None: cp = val
                except ValueError:
                    continue
                
            out = NISTOutput(cp=cp, h=h, s=s, g=g)
            
            # Cache for 24h using proper UltronRedis TTL arg
            await self.redis.set(cache_key, out.model_dump_json(), ex=86400)
            
            return out

# Instantiate at module level for auto-discovery
import os
try:
    _url = os.environ.get("UPSTASH_REDIS_REST_URL", "http://localhost")
    _token = os.environ.get("UPSTASH_REDIS_REST_TOKEN", "token")
    _redis_client = UltronRedis(url=_url, token=_token)
    nist_tool_instance = NISTChemistryTool(redis=_redis_client)
except Exception:
    pass
