from mcp.server import Server
import mcp.server.stdio
import mcp.types as types
import httpx

app = Server("pubchem_mcp")

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name != "get_compound_data":
        raise ValueError(f"Unknown tool: {name}")

    compound = arguments.get("name")
    if not compound:
        raise ValueError("Missing compound name")

    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{compound}/JSON"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        
        if response.status_code != 200:
            return [types.TextContent(type="text", text="Compound not found in PubChem.")]

        data = response.json()
        properties = data.get("PC_Compounds", [{}])[0].get("props", [])
        
        output = []
        for prop in properties:
            label = prop.get("urn", {}).get("label")
            if label in ["Molecular Weight", "Formula", "SMILES", "InChI"]:
                val = prop.get("value", {})
                v = val.get("sval") or val.get("fval")
                output.append(f"{label}: {v}")
                
        return [types.TextContent(type="text", text="\n".join(output))]

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_compound_data",
            description="Fetches compound data from PubChem.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Compound name"}
                },
                "required": ["name"]
            }
        )
    ]

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
