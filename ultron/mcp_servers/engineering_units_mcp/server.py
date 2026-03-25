from mcp.server import Server
import mcp.server.stdio
import mcp.types as types
from pint import UnitRegistry

app = Server("engineering_units_mcp")
ureg = UnitRegistry()

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name != "convert_units":
        raise ValueError(f"Unknown tool: {name}")

    value = arguments.get("value")
    from_unit = arguments.get("from_unit")
    to_unit = arguments.get("to_unit")
    
    if value is None or not from_unit or not to_unit:
        raise ValueError("Missing required arguments")

    try:
        qty = value * ureg(from_unit)
        converted = qty.to(to_unit)
        result_text = f"{value} {from_unit} = {converted.magnitude} {to_unit}"
        return [types.TextContent(type="text", text=result_text)]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Conversion error: {str(e)}")]

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="convert_units",
            description="Converts engineering units using Pint.",
            inputSchema={
                "type": "object",
                "properties": {
                    "value": {"type": "number"},
                    "from_unit": {"type": "string"},
                    "to_unit": {"type": "string"}
                },
                "required": ["value", "from_unit", "to_unit"]
            }
        )
    ]

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
