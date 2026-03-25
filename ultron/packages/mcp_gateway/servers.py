from typing import List, Optional
from pydantic import BaseModel

class MCPServerConfig(BaseModel):
    name: str
    url: str
    auth_env_var: Optional[str] = None
    capabilities: List[str]
    rate_limit_rpm: int
    fallback: Optional[str] = None

ALL_SERVERS: List[MCPServerConfig] = [
    MCPServerConfig(name="github", url="http://localhost:3001/github", auth_env_var="GITHUB_TOKEN", capabilities=["git", "repo"], rate_limit_rpm=5000),
    MCPServerConfig(name="semgrep", url="http://localhost:3002/semgrep", auth_env_var=None, capabilities=["security", "ast"], rate_limit_rpm=600),
    MCPServerConfig(name="context7", url="http://localhost:3003/context7", auth_env_var="CONTEXT7_KEY", capabilities=["rag", "search"], rate_limit_rpm=1000),
    MCPServerConfig(name="playwright", url="http://localhost:3004/playwright", auth_env_var=None, capabilities=["browser"], rate_limit_rpm=120),
    MCPServerConfig(name="arxiv", url="http://localhost:3005/arxiv", auth_env_var=None, capabilities=["academic"], rate_limit_rpm=60),
    MCPServerConfig(name="firecrawl", url="http://localhost:3006/firecrawl", auth_env_var="FIRECRAWL_KEY", capabilities=["scrape"], rate_limit_rpm=1000),
    MCPServerConfig(name="apify", url="http://localhost:3007/apify", auth_env_var="APIFY_KEY", capabilities=["actors"], rate_limit_rpm=300),
    MCPServerConfig(name="fastio", url="http://localhost:3008/fastio", auth_env_var="FASTIO_KEY", capabilities=["storage"], rate_limit_rpm=500),
    MCPServerConfig(name="n8n", url="http://localhost:3009/n8n", auth_env_var="N8N_KEY", capabilities=["workflow"], rate_limit_rpm=100),
    MCPServerConfig(name="notion", url="http://localhost:3010/notion", auth_env_var="NOTION_TOKEN", capabilities=["docs"], rate_limit_rpm=180),
    MCPServerConfig(name="nist_mcp", url="http://localhost:3011/nist", auth_env_var=None, capabilities=["thermochem"], rate_limit_rpm=600),
    MCPServerConfig(name="pubchem_mcp", url="http://localhost:3012/pubchem", auth_env_var=None, capabilities=["compounds"], rate_limit_rpm=600),
    MCPServerConfig(name="engineering_units_mcp", url="http://localhost:3013/units", auth_env_var=None, capabilities=["conversion"], rate_limit_rpm=6000),
    MCPServerConfig(name="bifrost", url="http://localhost:3014/bifrost", auth_env_var="BIFROST_KEY", capabilities=["router"], rate_limit_rpm=10000),
    MCPServerConfig(name="e2b", url="http://localhost:3015/e2b", auth_env_var="E2B_KEY", capabilities=["sandbox"], rate_limit_rpm=600),
    MCPServerConfig(name="mem0", url="http://localhost:3016/mem0", auth_env_var="MEM0_KEY", capabilities=["memory"], rate_limit_rpm=1000),
]
