from mcp_use import MCPAgent, MCPClient
config = {
        "mcpServers": {
            "sql": {
                "command": "uv",
                "args": ["--directory", "C:/Users/Tejas/Documents/Project/MCP/mcp-database-webui-main/mcp-database-webui-main/mcp-server", "run", "main.py"],
                "env": {
                    "DB_HOST": "localhost",
                    "DB_PORT": "3306",
                    "DB_USER": "root",
                    "DB_PASSWORD": "Abcd@4321",
                    "DB_NAME": "Customers"
                }
            }
        }
    }
client = MCPClient.from_dict(config)
print(f"Available tools: {client.tools}")
