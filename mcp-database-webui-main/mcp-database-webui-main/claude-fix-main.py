import asyncio
import os
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic

from mcp_use import MCPAgent, MCPClient

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes

# Load environment variables
load_dotenv()

# MySQL connection parameters
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "Customers")

def create_agent():
    # Create configuration dictionary for MySQL MCP server
    config = {
        "mcpServers": {
            "sql": {
                "command": "uv",
                "args": ["--directory", "C:/Users/arpbhusa/Documents/Project/MCP/mcp-database-webui-main/mcp-database-webui-main/mcp-server", "run", "main.py"],
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
    
    try:
        # Create MCPClient from configuration dictionary
        client = MCPClient.from_dict(config)
        
        # Create Anthropic LLM
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",  # Use a stable model version
            temperature=0.1,  # Lower temperature for more consistent results
            max_tokens=2048,
            timeout=30,
            max_retries=2
        )
        
        # Create agent with the client
        agent = MCPAgent(llm=llm, client=client, max_steps=30)
        print("✅ Agent created successfully")
        return agent
        
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise

async def run_agent_query(query):
    try:
        agent = create_agent()
        
        # Add context about the database schema
        full_query = f"""
You are working with MySQL 9.3.0 database named `Customers`.

SEARCH BEST PRACTICES:
- Always use CASE-INSENSITIVE searches with LOWER() function
- Use LIKE with % wildcards for partial matches
- For company/brand searches, use flexible patterns

SEARCH EXAMPLES:
- For "adidas": WHERE LOWER(name) LIKE '%adidas%'
- For "cape union": WHERE LOWER(name) LIKE '%cape%union%' OR LOWER(name) LIKE '%cape union%'
- For partial names: WHERE LOWER(name) LIKE LOWER('%search_term%')

FORBIDDEN SQL FUNCTIONS:
- PERCENTILE_CONT() ❌
- PERCENTILE_DISC() ❌ 
- WITHIN GROUP ❌

ALLOWED MySQL FUNCTIONS:
- ROW_NUMBER() OVER() ✅
- COUNT() OVER() ✅
- AVG(), MAX(), MIN() ✅
- LOWER(), UPPER() ✅
- LIKE with % wildcards ✅

For median calculation, use:
```sql
SELECT age FROM (
  SELECT age, ROW_NUMBER() OVER (ORDER BY age) as row_num,
         COUNT(*) OVER () as total_count
  FROM employee
) ranked
WHERE row_num = CEIL(total_count / 2.0)
```

User question: {query}

Always construct queries that handle partial matches and case insensitivity.
First, get the database schema to understand the available tables and columns.
"""
        
        print(f"🔄 Running query: {query}")
        result = await agent.run(full_query)
        print(f"✅ Query completed successfully")
        
        return {"status": "success", "result": result}
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error in run_agent_query: {error_msg}")
        print(f"Traceback: {traceback.format_exc()}")
        
        # Check for specific error patterns
        if "'dict' object has no attribute 'tool'" in error_msg:
            error_msg = "MCP tool configuration error. Please check if the MCP server is running and tools are properly registered."
        
        return {"status": "error", "message": error_msg}

@app.route('/api/query', methods=['POST'])
def handle_query():
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({"status": "error", "message": "No query provided"}), 400
        
        query = data['query']
        
        # Run the async function in the Flask context
        result = asyncio.run(run_agent_query(query))
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Error in handle_query: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test agent creation
        agent = create_agent()
        return jsonify({"status": "healthy", "message": "Agent created successfully"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "message": str(e)}), 500

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == "__main__":
    print("🚀 Starting Flask application...")
    app.run(debug=True, port=5000)