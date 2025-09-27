# Python MCP

The Model Context Protocol (MCP) is an open standard that enables seamless  
communication between AI applications and external data sources. MCP allows  
AI models to securely connect to databases, APIs, file systems, and other  
resources through a standardized interface.  

MCP bridges the gap between AI models and the real world, providing structured  
access to external information while maintaining security and control. It  
enables developers to build AI applications that can interact with live data,  
execute operations, and maintain context across conversations.  

```bash
pip install mcp
```

## What is MCP?

MCP (Model Context Protocol) is a universal protocol for connecting AI  
assistants to data sources and tools. It provides:  

- **Standardized Communication**: Consistent interface across different systems  
- **Security**: Controlled access to resources with proper authentication  
- **Extensibility**: Support for custom tools and data sources  
- **Real-time Access**: Live connections to databases and APIs  
- **Context Preservation**: Maintains conversation state and history  

Think of MCP as a universal translator that allows AI models to speak with  
databases, file systems, web services, and custom tools using a common language.  

## Core Components

**Server**: Exposes resources, tools, and prompts to MCP clients  
**Client**: Connects to MCP servers to access their capabilities  
**Transport**: Communication layer (stdio, SSE, or WebSocket)  
**Resources**: Data sources like files, databases, or API endpoints  
**Tools**: Functions that can be executed by the AI model  
**Prompts**: Templates and prompt fragments for AI interactions  

## Basic Server Setup

This example demonstrates creating a basic MCP server that exposes a simple  
greeting resource and calculation tool.  

```python
#!/usr/bin/env python3
import asyncio
import json
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent


# Initialize the MCP server
app = Server("basic-demo")

@app.list_resources()
async def handle_list_resources() -> list[Resource]:
    """Return list of available resources."""
    return [
        Resource(
            uri="demo://greeting",
            name="Greeting Resource",
            description="A simple greeting message",
            mimeType="text/plain"
        )
    ]

@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read content from a resource."""
    if uri == "demo://greeting":
        return "Hello there! Welcome to MCP with Python."
    else:
        raise ValueError(f"Unknown resource: {uri}")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Return list of available tools."""
    return [
        Tool(
            name="calculator",
            description="Perform basic arithmetic calculations",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string", 
                        "enum": ["add", "subtract", "multiply", "divide"]
                    },
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["operation", "a", "b"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool with given arguments."""
    if name == "calculator":
        operation = arguments["operation"]
        a = arguments["a"]
        b = arguments["b"]
        
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                return [TextContent(type="text", text="Error: Division by zero")]
            result = a / b
        else:
            return [TextContent(type="text", text=f"Unknown operation: {operation}")]
            
        return [TextContent(type="text", text=f"Result: {result}")]
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the MCP server using stdio transport."""
    options = InitializationOptions(
        server_name="basic-demo",
        server_version="1.0.0",
        capabilities={
            "resources": {},
            "tools": {}
        }
    )
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream, 
            write_stream, 
            options
        )

if __name__ == "__main__":
    asyncio.run(main())
```

This basic server demonstrates the fundamental MCP patterns: resource listing  
and reading, tool definition and execution. The server runs over stdio transport,  
making it suitable for integration with various MCP clients. The calculator tool  
showcases parameter validation and error handling within MCP operations.  

## File System Server

This example creates an MCP server that provides secure access to file system  
operations, demonstrating resource management and file manipulation tools.  

```python
#!/usr/bin/env python3
import asyncio
import os
import json
from pathlib import Path
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent


# Initialize file system MCP server
app = Server("filesystem-server")

# Configure allowed directories for security
ALLOWED_DIRECTORIES = [
    "/tmp/mcp-demo",
    os.path.expanduser("~/Documents/mcp-files")
]

def is_path_allowed(path: str) -> bool:
    """Check if path is within allowed directories."""
    abs_path = os.path.abspath(path)
    return any(abs_path.startswith(allowed) for allowed in ALLOWED_DIRECTORIES)

@app.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List all files in allowed directories as resources."""
    resources = []
    
    for base_dir in ALLOWED_DIRECTORIES:
        if os.path.exists(base_dir):
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, base_dir)
                    
                    resources.append(Resource(
                        uri=f"file://{file_path}",
                        name=rel_path,
                        description=f"File: {rel_path}",
                        mimeType="text/plain"
                    ))
    
    return resources

@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read content from a file resource."""
    if not uri.startswith("file://"):
        raise ValueError("Only file:// URIs are supported")
    
    file_path = uri[7:]  # Remove "file://" prefix
    
    if not is_path_allowed(file_path):
        raise ValueError("Access denied: Path not in allowed directories")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")
    except Exception as e:
        raise ValueError(f"Error reading file: {str(e)}")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Return list of file system tools."""
    return [
        Tool(
            name="create_file",
            description="Create a new file with specified content",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path"},
                    "content": {"type": "string", "description": "File content"}
                },
                "required": ["path", "content"]
            }
        ),
        Tool(
            name="list_directory",
            description="List contents of a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path"}
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="delete_file",
            description="Delete a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to delete"}
                },
                "required": ["path"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute file system operations."""
    
    if name == "create_file":
        path = arguments["path"]
        content = arguments["content"]
        
        if not is_path_allowed(path):
            return [TextContent(
                type="text", 
                text="Error: Path not in allowed directories"
            )]
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return [TextContent(
                type="text", 
                text=f"File created successfully: {path}"
            )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error creating file: {str(e)}")]
    
    elif name == "list_directory":
        path = arguments["path"]
        
        if not is_path_allowed(path):
            return [TextContent(
                type="text", 
                text="Error: Path not in allowed directories"
            )]
        
        try:
            items = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    items.append(f"📁 {item}/")
                else:
                    items.append(f"📄 {item}")
            
            return [TextContent(
                type="text", 
                text=f"Contents of {path}:\n" + "\n".join(items)
            )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error listing directory: {str(e)}")]
    
    elif name == "delete_file":
        path = arguments["path"]
        
        if not is_path_allowed(path):
            return [TextContent(
                type="text", 
                text="Error: Path not in allowed directories"
            )]
        
        try:
            os.remove(path)
            return [TextContent(
                type="text", 
                text=f"File deleted successfully: {path}"
            )]
        except FileNotFoundError:
            return [TextContent(type="text", text=f"File not found: {path}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error deleting file: {str(e)}")]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the file system MCP server."""
    # Ensure allowed directories exist
    for directory in ALLOWED_DIRECTORIES:
        os.makedirs(directory, exist_ok=True)
    
    options = InitializationOptions(
        server_name="filesystem-server",
        server_version="1.0.0",
        capabilities={
            "resources": {},
            "tools": {}
        }
    )
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, options)

if __name__ == "__main__":
    asyncio.run(main())
```

This file system server demonstrates security-first MCP design with path  
validation and sandboxed operations. It exposes files as resources and provides  
tools for common file operations. The server maintains strict access control  
by only allowing operations within predefined directories, preventing  
unauthorized file system access.  

## Database Connection Server

This example shows how to create an MCP server that connects to a database  
and provides query capabilities through tools and data access through resources.  

```python
#!/usr/bin/env python3
import asyncio
import sqlite3
import json
from typing import List, Dict, Any
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent


# Initialize database MCP server
app = Server("database-server")

# Database connection
DB_PATH = "/tmp/mcp_demo.db"

def init_database():
    """Initialize demo database with sample data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            product TEXT NOT NULL,
            amount DECIMAL(10,2),
            order_date DATE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Insert sample data if tables are empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        sample_users = [
            ("Alice Johnson", "alice@example.com", 28),
            ("Bob Smith", "bob@example.com", 35),
            ("Carol Davis", "carol@example.com", 42)
        ]
        cursor.executemany("INSERT INTO users (name, email, age) VALUES (?, ?, ?)", sample_users)
        
        sample_orders = [
            (1, "Laptop", 999.99, "2024-01-15"),
            (1, "Mouse", 25.50, "2024-01-16"),
            (2, "Keyboard", 75.00, "2024-01-20"),
            (3, "Monitor", 299.99, "2024-01-22")
        ]
        cursor.executemany("INSERT INTO orders (user_id, product, amount, order_date) VALUES (?, ?, ?, ?)", sample_orders)
    
    conn.commit()
    conn.close()

@app.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List database tables as resources."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    resources = []
    for (table_name,) in tables:
        resources.append(Resource(
            uri=f"db://table/{table_name}",
            name=f"Table: {table_name}",
            description=f"Database table: {table_name}",
            mimeType="application/json"
        ))
    
    conn.close()
    return resources

@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read data from database table."""
    if not uri.startswith("db://table/"):
        raise ValueError("Only db://table/ URIs are supported")
    
    table_name = uri.split("/")[-1]
    
    # Validate table name to prevent SQL injection
    if not table_name.isalnum():
        raise ValueError("Invalid table name")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 100")
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        data = [dict(row) for row in rows]
        
        return json.dumps(data, indent=2, default=str)
    
    except sqlite3.Error as e:
        raise ValueError(f"Database error: {str(e)}")
    finally:
        conn.close()

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Return list of database tools."""
    return [
        Tool(
            name="execute_query",
            description="Execute a SELECT query on the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "SQL SELECT query"},
                    "params": {
                        "type": "array", 
                        "description": "Query parameters",
                        "items": {"type": ["string", "number", "null"]}
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_schema",
            description="Get database schema information",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string", 
                        "description": "Table name (optional)"
                    }
                }
            }
        ),
        Tool(
            name="insert_user",
            description="Insert a new user record",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "age": {"type": "integer"}
                },
                "required": ["name", "email"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute database operations."""
    
    if name == "execute_query":
        query = arguments["query"]
        params = arguments.get("params", [])
        
        # Basic SQL injection protection - only allow SELECT statements
        if not query.strip().upper().startswith("SELECT"):
            return [TextContent(
                type="text", 
                text="Error: Only SELECT queries are allowed"
            )]
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            if rows:
                data = [dict(row) for row in rows]
                result = json.dumps(data, indent=2, default=str)
            else:
                result = "No results found"
            
            return [TextContent(type="text", text=result)]
        
        except sqlite3.Error as e:
            return [TextContent(type="text", text=f"Database error: {str(e)}")]
        finally:
            conn.close()
    
    elif name == "get_schema":
        table_name = arguments.get("table_name")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        try:
            if table_name:
                cursor.execute("PRAGMA table_info(?)", (table_name,))
                columns = cursor.fetchall()
                schema_info = {
                    "table": table_name,
                    "columns": [
                        {
                            "name": col[1],
                            "type": col[2],
                            "nullable": not col[3],
                            "primary_key": bool(col[5])
                        }
                        for col in columns
                    ]
                }
            else:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                schema_info = {"tables": tables}
            
            return [TextContent(
                type="text", 
                text=json.dumps(schema_info, indent=2)
            )]
        
        except sqlite3.Error as e:
            return [TextContent(type="text", text=f"Database error: {str(e)}")]
        finally:
            conn.close()
    
    elif name == "insert_user":
        name = arguments["name"]
        email = arguments["email"]
        age = arguments.get("age")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                (name, email, age)
            )
            conn.commit()
            user_id = cursor.lastrowid
            
            return [TextContent(
                type="text", 
                text=f"User created successfully with ID: {user_id}"
            )]
        
        except sqlite3.IntegrityError:
            return [TextContent(
                type="text", 
                text=f"Error: Email {email} already exists"
            )]
        except sqlite3.Error as e:
            return [TextContent(type="text", text=f"Database error: {str(e)}")]
        finally:
            conn.close()
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the database MCP server."""
    init_database()
    
    options = InitializationOptions(
        server_name="database-server",
        server_version="1.0.0",
        capabilities={
            "resources": {},
            "tools": {}
        }
    )
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, options)

if __name__ == "__main__":
    asyncio.run(main())
```

This database server demonstrates secure database access patterns in MCP.  
It provides read-only query execution with SQL injection protection, schema  
introspection tools, and controlled write operations. Tables are exposed as  
resources for easy data access, while tools enable dynamic queries and  
data manipulation within security constraints.  

## Basic MCP Client

This example shows how to create an MCP client that connects to and interacts  
with MCP servers to access their resources and tools.  

```python
#!/usr/bin/env python3
import asyncio
import json
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client


class MCPClient:
    def __init__(self):
        self.session = None
    
    async def connect(self, command: list[str]):
        """Connect to MCP server via stdio."""
        self.stdio_client = stdio_client(command)
        self.read_stream, self.write_stream = await self.stdio_client.__aenter__()
        
        self.session = ClientSession(self.read_stream, self.write_stream)
        await self.session.initialize()
        
        print("✅ Connected to MCP server")
        return self
    
    async def disconnect(self):
        """Disconnect from MCP server."""
        if self.session:
            await self.session.close()
        await self.stdio_client.__aexit__(None, None, None)
        print("👋 Disconnected from MCP server")
    
    async def list_resources(self):
        """List all available resources."""
        result = await self.session.list_resources()
        
        print("\n📚 Available Resources:")
        for resource in result.resources:
            print(f"  • {resource.name}")
            print(f"    URI: {resource.uri}")
            print(f"    Description: {resource.description}")
            print()
        
        return result.resources
    
    async def read_resource(self, uri: str):
        """Read content from a resource."""
        result = await self.session.read_resource(uri)
        
        print(f"\n📖 Resource Content ({uri}):")
        for content in result.contents:
            if hasattr(content, 'text'):
                print(content.text)
            else:
                print(f"Binary content: {len(content.blob)} bytes")
        
        return result.contents
    
    async def list_tools(self):
        """List all available tools."""
        result = await self.session.list_tools()
        
        print("\n🔧 Available Tools:")
        for tool in result.tools:
            print(f"  • {tool.name}")
            print(f"    Description: {tool.description}")
            if hasattr(tool, 'inputSchema'):
                print(f"    Input Schema: {json.dumps(tool.inputSchema, indent=6)}")
            print()
        
        return result.tools
    
    async def call_tool(self, name: str, arguments: dict):
        """Call a tool with specified arguments."""
        result = await self.session.call_tool(name, arguments)
        
        print(f"\n🛠️  Tool Result ({name}):")
        for content in result.content:
            if hasattr(content, 'text'):
                print(content.text)
            else:
                print(f"Binary result: {len(content.blob)} bytes")
        
        return result.content
    
    async def interactive_session(self):
        """Run interactive session with the MCP server."""
        print("\n🤖 Interactive MCP Session")
        print("Commands: resources, tools, read <uri>, call <tool> <args>, quit")
        
        while True:
            try:
                command = input("\n> ").strip().split()
                if not command:
                    continue
                
                if command[0] == "quit":
                    break
                elif command[0] == "resources":
                    await self.list_resources()
                elif command[0] == "tools":
                    await self.list_tools()
                elif command[0] == "read" and len(command) > 1:
                    await self.read_resource(command[1])
                elif command[0] == "call" and len(command) > 2:
                    tool_name = command[1]
                    try:
                        args = json.loads(" ".join(command[2:]))
                        await self.call_tool(tool_name, args)
                    except json.JSONDecodeError:
                        print("❌ Invalid JSON arguments")
                else:
                    print("❌ Unknown command")
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")

async def main():
    """Demo MCP client usage."""
    # Connect to the basic demo server
    server_command = ["python3", "basic_server.py"]
    
    client = MCPClient()
    try:
        await client.connect(server_command)
        
        # Demonstrate basic operations
        resources = await client.list_resources()
        tools = await client.list_tools()
        
        # Read a resource
        if resources:
            await client.read_resource(resources[0].uri)
        
        # Call a tool
        if tools:
            await client.call_tool("calculator", {
                "operation": "add",
                "a": 10,
                "b": 5
            })
        
        # Start interactive session
        await client.interactive_session()
        
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

This client demonstrates the essential MCP client patterns: connection  
management, resource discovery and access, tool discovery and execution.  
The interactive session allows real-time exploration of server capabilities,  
making it useful for testing and debugging MCP implementations.  

## HTTP API Server Integration

This example shows how to create an MCP server that integrates with external  
HTTP APIs, providing AI models access to live web services and data.  

```python
#!/usr/bin/env python3
import asyncio
import aiohttp
import json
from typing import Optional
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent


# Initialize HTTP API MCP server
app = Server("http-api-server")

# Configuration
API_BASE_URL = "https://api.github.com"
API_TIMEOUT = 30

@app.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available API endpoints as resources."""
    return [
        Resource(
            uri="api://github/user",
            name="GitHub User Profile",
            description="Current authenticated user's GitHub profile",
            mimeType="application/json"
        ),
        Resource(
            uri="api://github/repos",
            name="GitHub Repositories",
            description="User's GitHub repositories",
            mimeType="application/json"
        ),
        Resource(
            uri="api://weather/current",
            name="Current Weather",
            description="Current weather data",
            mimeType="application/json"
        )
    ]

@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Fetch data from external APIs."""
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)) as session:
        
        if uri == "api://github/user":
            headers = {"Accept": "application/vnd.github.v3+json"}
            # Note: In production, use proper authentication
            async with session.get(f"{API_BASE_URL}/user", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return json.dumps(data, indent=2)
                else:
                    return f"Error: HTTP {response.status}"
        
        elif uri == "api://github/repos":
            headers = {"Accept": "application/vnd.github.v3+json"}
            async with session.get(f"{API_BASE_URL}/user/repos", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return json.dumps(data[:10], indent=2)  # Limit to first 10 repos
                else:
                    return f"Error: HTTP {response.status}"
        
        elif uri == "api://weather/current":
            # Mock weather API response
            weather_data = {
                "location": "San Francisco, CA",
                "temperature": "22°C",
                "condition": "Partly Cloudy",
                "humidity": "65%",
                "wind": "12 km/h NW",
                "last_updated": "2024-01-15 14:30:00"
            }
            return json.dumps(weather_data, indent=2)
        
        else:
            raise ValueError(f"Unknown resource: {uri}")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Return list of API interaction tools."""
    return [
        Tool(
            name="github_search",
            description="Search GitHub repositories",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "sort": {
                        "type": "string", 
                        "enum": ["stars", "forks", "updated"],
                        "description": "Sort order"
                    },
                    "limit": {
                        "type": "integer", 
                        "minimum": 1, 
                        "maximum": 100,
                        "description": "Number of results"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="http_request",
            description="Make generic HTTP request",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Request URL"},
                    "method": {
                        "type": "string", 
                        "enum": ["GET", "POST", "PUT", "DELETE"],
                        "description": "HTTP method"
                    },
                    "headers": {
                        "type": "object",
                        "description": "Request headers"
                    },
                    "data": {"description": "Request body data"}
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="weather_forecast",
            description="Get weather forecast for a location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name or coordinates"},
                    "days": {
                        "type": "integer", 
                        "minimum": 1, 
                        "maximum": 7,
                        "description": "Number of forecast days"
                    }
                },
                "required": ["location"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute API calls and external requests."""
    
    if name == "github_search":
        query = arguments["query"]
        sort = arguments.get("sort", "stars")
        limit = arguments.get("limit", 10)
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)) as session:
            search_url = f"{API_BASE_URL}/search/repositories"
            params = {
                "q": query,
                "sort": sort,
                "order": "desc",
                "per_page": limit
            }
            headers = {"Accept": "application/vnd.github.v3+json"}
            
            try:
                async with session.get(search_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        results = []
                        for repo in data.get("items", []):
                            results.append({
                                "name": repo["full_name"],
                                "description": repo.get("description", "No description"),
                                "stars": repo["stargazers_count"],
                                "forks": repo["forks_count"],
                                "url": repo["html_url"]
                            })
                        
                        return [TextContent(
                            type="text",
                            text=json.dumps(results, indent=2)
                        )]
                    else:
                        return [TextContent(
                            type="text",
                            text=f"Error: GitHub API returned status {response.status}"
                        )]
            
            except asyncio.TimeoutError:
                return [TextContent(
                    type="text",
                    text="Error: Request timed out"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
    
    elif name == "http_request":
        url = arguments["url"]
        method = arguments.get("method", "GET").upper()
        headers = arguments.get("headers", {})
        data = arguments.get("data")
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)) as session:
            try:
                async with session.request(
                    method, 
                    url, 
                    headers=headers,
                    json=data if data else None
                ) as response:
                    response_text = await response.text()
                    
                    result = {
                        "status": response.status,
                        "headers": dict(response.headers),
                        "body": response_text
                    }
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )]
            
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
    
    elif name == "weather_forecast":
        location = arguments["location"]
        days = arguments.get("days", 3)
        
        # Mock weather forecast data
        forecast_data = {
            "location": location,
            "forecast": [
                {
                    "date": "2024-01-15",
                    "high": "24°C",
                    "low": "18°C",
                    "condition": "Sunny",
                    "precipitation": "0%"
                },
                {
                    "date": "2024-01-16", 
                    "high": "26°C",
                    "low": "20°C",
                    "condition": "Partly Cloudy",
                    "precipitation": "10%"
                },
                {
                    "date": "2024-01-17",
                    "high": "23°C", 
                    "low": "17°C",
                    "condition": "Rainy",
                    "precipitation": "80%"
                }
            ][:days]
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(forecast_data, indent=2)
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the HTTP API MCP server."""
    options = InitializationOptions(
        server_name="http-api-server",
        server_version="1.0.0",
        capabilities={
            "resources": {},
            "tools": {}
        }
    )
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, options)

if __name__ == "__main__":
    asyncio.run(main())
```

This HTTP API server demonstrates how MCP can bridge AI models with external  
web services. It handles API authentication, request timeouts, error handling,  
and response formatting. The server exposes both static API endpoints as  
resources and dynamic API operations as tools, providing flexible access  
to external data sources.  

## WebSocket Real-time Server

This example creates an MCP server that handles real-time communications  
using WebSocket transport instead of stdio, suitable for web applications  
and real-time data streaming.  

```python
#!/usr/bin/env python3
import asyncio
import websockets
import json
import random
from datetime import datetime
from typing import Dict, Set
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Resource, Tool, TextContent


# Initialize WebSocket MCP server
app = Server("websocket-realtime-server")

# Store active connections and subscriptions
active_connections: Set[websockets.WebSocketServerProtocol] = set()
subscriptions: Dict[str, Set[websockets.WebSocketServerProtocol]] = {}

@app.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List real-time data streams as resources."""
    return [
        Resource(
            uri="stream://stock-prices",
            name="Stock Price Feed",
            description="Real-time stock price updates",
            mimeType="application/json"
        ),
        Resource(
            uri="stream://system-metrics",
            name="System Metrics",
            description="Real-time system performance metrics",
            mimeType="application/json"
        ),
        Resource(
            uri="stream://chat-messages",
            name="Chat Messages",
            description="Live chat message stream",
            mimeType="application/json"
        )
    ]

@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Get current snapshot of real-time data."""
    current_time = datetime.now().isoformat()
    
    if uri == "stream://stock-prices":
        stock_data = {
            "timestamp": current_time,
            "prices": {
                "AAPL": round(random.uniform(150, 200), 2),
                "GOOGL": round(random.uniform(100, 150), 2),
                "MSFT": round(random.uniform(250, 350), 2),
                "TSLA": round(random.uniform(200, 300), 2)
            }
        }
        return json.dumps(stock_data, indent=2)
    
    elif uri == "stream://system-metrics":
        metrics = {
            "timestamp": current_time,
            "cpu_usage": round(random.uniform(10, 90), 1),
            "memory_usage": round(random.uniform(30, 80), 1),
            "disk_usage": round(random.uniform(40, 95), 1),
            "network_io": {
                "bytes_sent": random.randint(1000, 10000),
                "bytes_received": random.randint(5000, 50000)
            }
        }
        return json.dumps(metrics, indent=2)
    
    elif uri == "stream://chat-messages":
        messages = {
            "timestamp": current_time,
            "recent_messages": [
                {
                    "id": "msg_001",
                    "user": "alice",
                    "message": "Hello there! How is everyone doing?",
                    "timestamp": current_time
                },
                {
                    "id": "msg_002", 
                    "user": "bob",
                    "message": "Great! Working on some interesting projects.",
                    "timestamp": current_time
                }
            ]
        }
        return json.dumps(messages, indent=2)
    
    else:
        raise ValueError(f"Unknown resource: {uri}")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Return list of real-time communication tools."""
    return [
        Tool(
            name="subscribe_stream",
            description="Subscribe to a real-time data stream",
            inputSchema={
                "type": "object",
                "properties": {
                    "stream": {
                        "type": "string",
                        "enum": ["stock-prices", "system-metrics", "chat-messages"],
                        "description": "Stream name to subscribe to"
                    },
                    "interval": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 60,
                        "description": "Update interval in seconds"
                    }
                },
                "required": ["stream"]
            }
        ),
        Tool(
            name="unsubscribe_stream",
            description="Unsubscribe from a real-time stream",
            inputSchema={
                "type": "object",
                "properties": {
                    "stream": {
                        "type": "string",
                        "description": "Stream name to unsubscribe from"
                    }
                },
                "required": ["stream"]
            }
        ),
        Tool(
            name="broadcast_message",
            description="Broadcast a message to all connected clients",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Message to broadcast"},
                    "channel": {"type": "string", "description": "Channel name"}
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="get_connection_stats",
            description="Get statistics about active connections",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute real-time communication operations."""
    
    if name == "subscribe_stream":
        stream = arguments["stream"]
        interval = arguments.get("interval", 5)
        
        # In a real implementation, this would set up the subscription
        subscription_info = {
            "stream": stream,
            "interval": interval,
            "status": "subscribed",
            "message": f"Successfully subscribed to {stream} with {interval}s updates"
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(subscription_info, indent=2)
        )]
    
    elif name == "unsubscribe_stream":
        stream = arguments["stream"]
        
        result = {
            "stream": stream,
            "status": "unsubscribed",
            "message": f"Successfully unsubscribed from {stream}"
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "broadcast_message":
        message = arguments["message"]
        channel = arguments.get("channel", "general")
        
        broadcast_data = {
            "type": "broadcast",
            "channel": channel,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "recipients": len(active_connections)
        }
        
        # In a real implementation, this would actually broadcast to connections
        return [TextContent(
            type="text",
            text=json.dumps(broadcast_data, indent=2)
        )]
    
    elif name == "get_connection_stats":
        stats = {
            "active_connections": len(active_connections),
            "total_subscriptions": sum(len(subs) for subs in subscriptions.values()),
            "streams": list(subscriptions.keys()),
            "uptime": "2h 15m 30s",  # Mock uptime
            "last_update": datetime.now().isoformat()
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(stats, indent=2)
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def handle_websocket_connection(websocket, path):
    """Handle individual WebSocket connections."""
    active_connections.add(websocket)
    print(f"✅ New connection: {websocket.remote_address}")
    
    try:
        # Initialize MCP session over WebSocket
        options = InitializationOptions(
            server_name="websocket-realtime-server",
            server_version="1.0.0",
            capabilities={
                "resources": {},
                "tools": {}
            }
        )
        
        # Handle MCP protocol over WebSocket
        await app.run_websocket(websocket, options)
        
    except websockets.exceptions.ConnectionClosed:
        print(f"🔌 Connection closed: {websocket.remote_address}")
    except Exception as e:
        print(f"❌ Error handling connection: {e}")
    finally:
        active_connections.discard(websocket)
        # Remove from all subscriptions
        for stream_subs in subscriptions.values():
            stream_subs.discard(websocket)

async def data_stream_generator():
    """Generate and broadcast real-time data updates."""
    while True:
        try:
            # Generate stock price updates
            if "stock-prices" in subscriptions and subscriptions["stock-prices"]:
                stock_update = {
                    "stream": "stock-prices",
                    "data": {
                        "timestamp": datetime.now().isoformat(),
                        "AAPL": round(random.uniform(150, 200), 2),
                        "GOOGL": round(random.uniform(100, 150), 2)
                    }
                }
                
                # Send to subscribers (mock implementation)
                print(f"📊 Broadcasting stock update to {len(subscriptions.get('stock-prices', set()))} clients")
            
            # Generate system metrics
            if "system-metrics" in subscriptions and subscriptions["system-metrics"]:
                metrics_update = {
                    "stream": "system-metrics",
                    "data": {
                        "timestamp": datetime.now().isoformat(),
                        "cpu_usage": round(random.uniform(10, 90), 1),
                        "memory_usage": round(random.uniform(30, 80), 1)
                    }
                }
                
                print(f"💻 Broadcasting metrics to {len(subscriptions.get('system-metrics', set()))} clients")
            
            await asyncio.sleep(5)  # Update every 5 seconds
            
        except Exception as e:
            print(f"❌ Error in data stream: {e}")
            await asyncio.sleep(1)

async def main():
    """Start WebSocket MCP server with real-time data streaming."""
    print("🚀 Starting WebSocket MCP Server on localhost:8765")
    
    # Start data stream generator
    asyncio.create_task(data_stream_generator())
    
    # Start WebSocket server
    async with websockets.serve(handle_websocket_connection, "localhost", 8765):
        print("📡 Server is running... Press Ctrl+C to stop")
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            print("\n👋 Server shutting down...")

if __name__ == "__main__":
    asyncio.run(main())
```

This WebSocket server demonstrates real-time MCP capabilities over WebSocket  
transport. It manages multiple client connections, handles data stream  
subscriptions, and broadcasts updates in real-time. The server is ideal  
for applications requiring live data feeds like dashboards, monitoring  
systems, or collaborative tools.  

## Multi-Transport Server

This example shows how to create an MCP server that supports multiple  
transport protocols (stdio, WebSocket, SSE) simultaneously, providing  
maximum flexibility for different client types.  

```python
#!/usr/bin/env python3
import asyncio
import json
import websockets
from aiohttp import web, web_runner
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent


# Initialize multi-transport MCP server
app = Server("multi-transport-server")

@app.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available resources."""
    return [
        Resource(
            uri="info://server",
            name="Server Information",
            description="Information about the MCP server",
            mimeType="application/json"
        ),
        Resource(
            uri="info://transport",
            name="Transport Information",
            description="Active transport connections",
            mimeType="application/json"
        )
    ]

@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read server information."""
    if uri == "info://server":
        server_info = {
            "name": "Multi-Transport MCP Server",
            "version": "1.0.0",
            "supported_transports": ["stdio", "websocket", "sse"],
            "capabilities": ["resources", "tools"],
            "uptime": "1h 23m 45s"  # Mock uptime
        }
        return json.dumps(server_info, indent=2)
    
    elif uri == "info://transport":
        transport_info = {
            "active_connections": {
                "stdio": 1,
                "websocket": 3,
                "sse": 2
            },
            "total_requests": 156,
            "last_request": "2024-01-15 14:30:00"
        }
        return json.dumps(transport_info, indent=2)
    
    else:
        raise ValueError(f"Unknown resource: {uri}")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Return list of server management tools."""
    return [
        Tool(
            name="echo",
            description="Echo back the provided message",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Message to echo"},
                    "uppercase": {
                        "type": "boolean", 
                        "description": "Convert to uppercase"
                    }
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="get_transport_stats",
            description="Get detailed transport layer statistics",
            inputSchema={
                "type": "object",
                "properties": {
                    "transport": {
                        "type": "string",
                        "enum": ["stdio", "websocket", "sse", "all"],
                        "description": "Transport type to query"
                    }
                }
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute server tools."""
    
    if name == "echo":
        message = arguments["message"]
        uppercase = arguments.get("uppercase", False)
        
        result = message.upper() if uppercase else message
        
        return [TextContent(type="text", text=f"Echo: {result}")]
    
    elif name == "get_transport_stats":
        transport = arguments.get("transport", "all")
        
        if transport == "all":
            stats = {
                "stdio": {
                    "active_connections": 1,
                    "total_requests": 45,
                    "avg_response_time": "12ms"
                },
                "websocket": {
                    "active_connections": 3,
                    "total_requests": 89,
                    "avg_response_time": "8ms"
                },
                "sse": {
                    "active_connections": 2,
                    "total_requests": 22,
                    "avg_response_time": "15ms"
                }
            }
        else:
            stats = {
                transport: {
                    "active_connections": 2,
                    "total_requests": 67,
                    "avg_response_time": "10ms"
                }
            }
        
        return [TextContent(
            type="text",
            text=json.dumps(stats, indent=2)
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def stdio_handler():
    """Handle stdio transport."""
    options = InitializationOptions(
        server_name="multi-transport-server",
        server_version="1.0.0",
        capabilities={"resources": {}, "tools": {}}
    )
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, options)

async def websocket_handler(websocket, path):
    """Handle WebSocket transport."""
    try:
        options = InitializationOptions(
            server_name="multi-transport-server",
            server_version="1.0.0",
            capabilities={"resources": {}, "tools": {}}
        )
        
        await app.run_websocket(websocket, options)
        
    except websockets.exceptions.ConnectionClosed:
        pass

async def sse_handler(request):
    """Handle Server-Sent Events transport."""
    response = web.StreamResponse(
        status=200,
        reason='OK',
        headers={
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
    )
    
    await response.prepare(request)
    
    try:
        # Send initial connection event
        await response.write(b'data: {"type": "connected"}\n\n')
        
        # Handle MCP over SSE (simplified implementation)
        async for line in request.stream():
            try:
                # Process MCP messages over SSE
                data = json.loads(line.decode())
                
                # Echo back for demo purposes
                response_data = {
                    "type": "response",
                    "data": data,
                    "timestamp": "2024-01-15T14:30:00Z"
                }
                
                await response.write(
                    f"data: {json.dumps(response_data)}\n\n".encode()
                )
                
            except json.JSONDecodeError:
                continue
    
    except asyncio.CancelledError:
        pass
    
    return response

async def main():
    """Start multi-transport MCP server."""
    print("🚀 Starting Multi-Transport MCP Server")
    
    # Create tasks for different transports
    tasks = []
    
    # Optional: stdio transport (comment out if not needed)
    # tasks.append(asyncio.create_task(stdio_handler()))
    
    # WebSocket transport on port 8765
    websocket_server = websockets.serve(websocket_handler, "localhost", 8765)
    tasks.append(asyncio.create_task(websocket_server))
    print("📡 WebSocket server listening on localhost:8765")
    
    # HTTP/SSE transport on port 8080
    http_app = web.Application()
    http_app.router.add_get('/mcp/sse', sse_handler)
    http_app.router.add_get('/health', lambda r: web.Response(text="OK"))
    
    http_runner = web_runner.AppRunner(http_app)
    await http_runner.setup()
    
    http_site = web.TCPSite(http_runner, 'localhost', 8080)
    await http_site.start()
    print("🌐 HTTP/SSE server listening on localhost:8080")
    
    try:
        # Wait for all transport servers
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\n👋 Shutting down all transports...")
    finally:
        await http_runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

This multi-transport server provides maximum flexibility by supporting  
different communication protocols simultaneously. Clients can choose the  
most appropriate transport for their needs: stdio for command-line tools,  
WebSocket for web applications, or SSE for server-push scenarios.  

## Authentication and Security

This example demonstrates implementing authentication, authorization, and  
security best practices in MCP servers, including API key validation,  
rate limiting, and secure resource access.  

```python
#!/usr/bin/env python3
import asyncio
import hashlib
import hmac
import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent


# Security configuration
SECRET_KEY = "your-secret-key-here"
VALID_API_KEYS = {
    "admin-key-123": {"role": "admin", "permissions": ["read", "write", "admin"]},
    "user-key-456": {"role": "user", "permissions": ["read"]},
    "service-key-789": {"role": "service", "permissions": ["read", "write"]}
}

@dataclass
class RateLimitInfo:
    requests: List[float] = field(default_factory=list)
    limit: int = 60  # requests per minute
    window: int = 60  # seconds

# Rate limiting storage
rate_limits: Dict[str, RateLimitInfo] = {}

# Initialize secure MCP server
app = Server("secure-mcp-server")

def verify_signature(data: str, signature: str, secret: str) -> bool:
    """Verify HMAC signature for request validation."""
    expected = hmac.new(
        secret.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected)

def check_rate_limit(client_id: str) -> bool:
    """Check if client is within rate limits."""
    now = time.time()
    
    if client_id not in rate_limits:
        rate_limits[client_id] = RateLimitInfo()
    
    rate_info = rate_limits[client_id]
    
    # Remove old requests outside the window
    rate_info.requests = [req_time for req_time in rate_info.requests 
                         if now - req_time < rate_info.window]
    
    # Check if under limit
    if len(rate_info.requests) >= rate_info.limit:
        return False
    
    # Add current request
    rate_info.requests.append(now)
    return True

def authenticate_request(headers: Dict[str, str]) -> Optional[Dict[str, str]]:
    """Authenticate request using API key."""
    api_key = headers.get("x-api-key")
    
    if not api_key or api_key not in VALID_API_KEYS:
        return None
    
    return VALID_API_KEYS[api_key]

def check_permission(user_info: Dict[str, str], required_permission: str) -> bool:
    """Check if user has required permission."""
    return required_permission in user_info.get("permissions", [])

@app.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available resources with security considerations."""
    # In a real implementation, this would use request context
    # to determine user permissions and filter resources accordingly
    
    return [
        Resource(
            uri="secure://public-data",
            name="Public Data",
            description="Publicly accessible data",
            mimeType="application/json"
        ),
        Resource(
            uri="secure://private-data",
            name="Private Data", 
            description="Private data requiring authentication",
            mimeType="application/json"
        ),
        Resource(
            uri="secure://admin-data",
            name="Admin Data",
            description="Administrative data requiring admin permissions",
            mimeType="application/json"
        )
    ]

@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read resources with security checks."""
    # Mock authentication context
    # In real implementation, extract from request context
    mock_headers = {"x-api-key": "user-key-456"}
    user_info = authenticate_request(mock_headers)
    
    if not user_info:
        raise ValueError("Authentication required")
    
    # Check rate limiting
    if not check_rate_limit(mock_headers["x-api-key"]):
        raise ValueError("Rate limit exceeded")
    
    if uri == "secure://public-data":
        # Public data - no additional permissions needed
        return json.dumps({
            "message": "This is public data",
            "timestamp": time.time(),
            "access_level": "public"
        }, indent=2)
    
    elif uri == "secure://private-data":
        # Private data - requires read permission
        if not check_permission(user_info, "read"):
            raise ValueError("Insufficient permissions")
        
        return json.dumps({
            "message": "This is private data",
            "user_role": user_info["role"],
            "sensitive_info": "🔒 Confidential content",
            "access_level": "private"
        }, indent=2)
    
    elif uri == "secure://admin-data":
        # Admin data - requires admin permission
        if not check_permission(user_info, "admin"):
            raise ValueError("Admin permissions required")
        
        return json.dumps({
            "message": "This is administrative data",
            "system_info": {
                "active_users": 42,
                "server_stats": {"uptime": "7 days", "memory": "4.2GB"}
            },
            "access_level": "admin"
        }, indent=2)
    
    else:
        raise ValueError(f"Unknown resource: {uri}")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Return list of security-aware tools."""
    return [
        Tool(
            name="validate_token",
            description="Validate authentication token",
            inputSchema={
                "type": "object",
                "properties": {
                    "token": {"type": "string", "description": "Token to validate"},
                    "signature": {"type": "string", "description": "HMAC signature"}
                },
                "required": ["token", "signature"]
            }
        ),
        Tool(
            name="get_permissions",
            description="Get current user permissions",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="secure_operation",
            description="Perform operation requiring write permissions",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["create", "update", "delete"],
                        "description": "Operation to perform"
                    },
                    "data": {"description": "Operation data"}
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="audit_log",
            description="View audit log (admin only)",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "description": "Number of entries to return"
                    }
                }
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute tools with security enforcement."""
    
    # Mock authentication context
    mock_headers = {"x-api-key": "admin-key-123"}
    user_info = authenticate_request(mock_headers)
    
    if not user_info:
        return [TextContent(type="text", text="Error: Authentication required")]
    
    # Check rate limiting
    if not check_rate_limit(mock_headers["x-api-key"]):
        return [TextContent(type="text", text="Error: Rate limit exceeded")]
    
    if name == "validate_token":
        token = arguments["token"]
        signature = arguments["signature"]
        
        is_valid = verify_signature(token, signature, SECRET_KEY)
        
        result = {
            "token": token[:10] + "...",  # Truncate for security
            "valid": is_valid,
            "timestamp": time.time()
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_permissions":
        permissions_info = {
            "role": user_info["role"],
            "permissions": user_info["permissions"],
            "api_key": mock_headers["x-api-key"][:8] + "...",
            "rate_limit": {
                "remaining": rate_limits[mock_headers["x-api-key"]].limit - 
                           len(rate_limits[mock_headers["x-api-key"]].requests),
                "reset_time": time.time() + 60
            }
        }
        
        return [TextContent(type="text", text=json.dumps(permissions_info, indent=2))]
    
    elif name == "secure_operation":
        if not check_permission(user_info, "write"):
            return [TextContent(type="text", text="Error: Write permission required")]
        
        action = arguments["action"]
        data = arguments.get("data", {})
        
        operation_result = {
            "action": action,
            "status": "completed",
            "user": user_info["role"],
            "timestamp": time.time(),
            "data": data
        }
        
        return [TextContent(type="text", text=json.dumps(operation_result, indent=2))]
    
    elif name == "audit_log":
        if not check_permission(user_info, "admin"):
            return [TextContent(type="text", text="Error: Admin permission required")]
        
        limit = arguments.get("limit", 10)
        
        # Mock audit log entries
        audit_entries = [
            {
                "timestamp": time.time() - 3600,
                "user": "user-key-456",
                "action": "read_resource",
                "resource": "secure://private-data"
            },
            {
                "timestamp": time.time() - 1800,
                "user": "admin-key-123",
                "action": "secure_operation",
                "details": "create operation"
            },
            {
                "timestamp": time.time() - 900,
                "user": "service-key-789",
                "action": "call_tool",
                "tool": "validate_token"
            }
        ]
        
        return [TextContent(
            type="text", 
            text=json.dumps(audit_entries[:limit], indent=2)
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the secure MCP server."""
    print("🔒 Starting Secure MCP Server")
    print("Security features enabled:")
    print("  ✅ API Key authentication")
    print("  ✅ Role-based permissions")
    print("  ✅ Rate limiting")
    print("  ✅ HMAC signature validation")
    print("  ✅ Audit logging")
    
    options = InitializationOptions(
        server_name="secure-mcp-server",
        server_version="1.0.0",
        capabilities={
            "resources": {},
            "tools": {},
            "security": {
                "authentication": "api-key",
                "rate_limiting": True,
                "permissions": ["read", "write", "admin"]
            }
        }
    )
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, options)

if __name__ == "__main__":
    asyncio.run(main())
```

This secure MCP server demonstrates essential security patterns: API key  
authentication, role-based access control, rate limiting, and audit logging.  
It shows how to protect resources and tools based on user permissions,  
prevent abuse through rate limiting, and maintain security audit trails.  

## Custom Tool Integration

This example demonstrates creating custom tools that integrate with external  
systems and APIs, showing advanced parameter handling and response formatting.  

```python
#!/usr/bin/env python3
import asyncio
import subprocess
import json
import os
import tempfile
from typing import Any, Dict
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


app = Server("custom-tools-server")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Return list of custom integration tools."""
    return [
        Tool(
            name="execute_shell",
            description="Execute shell command safely",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command"},
                    "timeout": {"type": "integer", "default": 30},
                    "working_dir": {"type": "string", "description": "Working directory"}
                },
                "required": ["command"]
            }
        ),
        Tool(
            name="create_temporary_file",
            description="Create and write to a temporary file",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "File content"},
                    "extension": {"type": "string", "description": "File extension"},
                    "encoding": {"type": "string", "default": "utf-8"}
                },
                "required": ["content"]
            }
        ),
        Tool(
            name="format_json", 
            description="Format and validate JSON data",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {"description": "JSON data to format"},
                    "indent": {"type": "integer", "default": 2},
                    "sort_keys": {"type": "boolean", "default": False}
                },
                "required": ["data"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute custom tools."""
    
    if name == "execute_shell":
        command = arguments["command"]
        timeout = arguments.get("timeout", 30)
        working_dir = arguments.get("working_dir", os.getcwd())
        
        # Security: Whitelist allowed commands
        allowed_commands = ["ls", "pwd", "date", "whoami", "echo"]
        cmd_parts = command.split()
        if not cmd_parts or cmd_parts[0] not in allowed_commands:
            return [TextContent(
                type="text",
                text="Error: Command not allowed for security reasons"
            )]
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=working_dir
            )
            
            output = {
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "working_dir": working_dir
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(output, indent=2)
            )]
            
        except subprocess.TimeoutExpired:
            return [TextContent(
                type="text",
                text=f"Error: Command timed out after {timeout} seconds"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]
    
    elif name == "create_temporary_file":
        content = arguments["content"]
        extension = arguments.get("extension", "txt")
        encoding = arguments.get("encoding", "utf-8")
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix=f".{extension}",
                delete=False,
                encoding=encoding
            ) as tmp_file:
                tmp_file.write(content)
                tmp_path = tmp_file.name
            
            file_info = {
                "path": tmp_path,
                "size": len(content.encode(encoding)),
                "extension": extension,
                "encoding": encoding,
                "message": "Temporary file created successfully"
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(file_info, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]
    
    elif name == "format_json":
        data = arguments["data"]
        indent = arguments.get("indent", 2)
        sort_keys = arguments.get("sort_keys", False)
        
        try:
            # Parse and reformat JSON
            if isinstance(data, str):
                parsed = json.loads(data)
            else:
                parsed = data
            
            formatted = json.dumps(
                parsed,
                indent=indent,
                sort_keys=sort_keys,
                ensure_ascii=False
            )
            
            return [TextContent(type="text", text=formatted)]
            
        except json.JSONDecodeError as e:
            return [TextContent(
                type="text",
                text=f"Error: Invalid JSON - {str(e)}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the custom tools MCP server."""
    options = InitializationOptions(
        server_name="custom-tools-server",
        server_version="1.0.0",
        capabilities={"tools": {}}
    )
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, options)

if __name__ == "__main__":
    asyncio.run(main())
```

This example showcases creating custom tools that extend MCP functionality  
beyond basic operations. It demonstrates proper error handling, security  
considerations for shell execution, and integration with system utilities.  

## Prompt Template Server

This example shows how to create an MCP server that manages and serves  
AI prompt templates, enabling systematic prompt engineering and reuse.  

```python
#!/usr/bin/env python3
import asyncio
import json
import re
from typing import Dict, List
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent, Prompt


# Prompt template storage
PROMPT_TEMPLATES = {
    "code-review": {
        "name": "Code Review",
        "description": "Template for systematic code reviews",
        "template": """Review this code for:
1. Functionality and correctness
2. Security vulnerabilities  
3. Performance issues
4. Code style and best practices
5. Documentation quality

Code to review:
```{language}
{code}
```

Focus areas: {focus_areas}
""",
        "variables": ["language", "code", "focus_areas"],
        "category": "development"
    },
    "bug-analysis": {
        "name": "Bug Analysis",
        "description": "Template for systematic bug investigation",
        "template": """Analyze this bug report systematically:

**Bug Description:**
{description}

**Expected Behavior:**
{expected}

**Actual Behavior:**
{actual}

**Environment:**
- Platform: {platform}
- Version: {version}
- Browser: {browser}

**Steps to Reproduce:**
{steps}

Please provide:
1. Root cause analysis
2. Potential fixes
3. Prevention strategies
4. Testing recommendations
""",
        "variables": ["description", "expected", "actual", "platform", "version", "browser", "steps"],
        "category": "debugging"
    },
    "documentation": {
        "name": "Documentation Generator",
        "description": "Template for generating comprehensive documentation",
        "template": """Generate documentation for this {component_type}:

**Component:** {component_name}

**Purpose:** 
{purpose}

**Technical Details:**
{technical_details}

Please create documentation including:
- Overview and purpose
- Installation/setup instructions  
- Usage examples
- API reference (if applicable)
- Configuration options
- Troubleshooting guide
- Contributing guidelines

Target audience: {audience}
Documentation format: {format}
""",
        "variables": ["component_type", "component_name", "purpose", "technical_details", "audience", "format"],
        "category": "documentation"
    }
}

app = Server("prompt-template-server")

@app.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List prompt templates as resources."""
    resources = []
    
    for template_id, template_data in PROMPT_TEMPLATES.items():
        resources.append(Resource(
            uri=f"prompt://{template_id}",
            name=template_data["name"],
            description=template_data["description"],
            mimeType="text/plain"
        ))
    
    return resources

@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read prompt template content."""
    if not uri.startswith("prompt://"):
        raise ValueError("Only prompt:// URIs are supported")
    
    template_id = uri.replace("prompt://", "")
    
    if template_id not in PROMPT_TEMPLATES:
        raise ValueError(f"Unknown template: {template_id}")
    
    template_data = PROMPT_TEMPLATES[template_id]
    
    return json.dumps({
        "template": template_data["template"],
        "variables": template_data["variables"],
        "category": template_data["category"],
        "usage": f"Use the 'render_prompt' tool to fill in variables: {', '.join(template_data['variables'])}"
    }, indent=2)

@app.list_prompts()
async def handle_list_prompts() -> list[Prompt]:
    """List available prompt templates."""
    prompts = []
    
    for template_id, template_data in PROMPT_TEMPLATES.items():
        # Create prompt arguments schema
        arguments_schema = {
            "type": "object",
            "properties": {},
            "required": template_data["variables"]
        }
        
        for var in template_data["variables"]:
            arguments_schema["properties"][var] = {
                "type": "string",
                "description": f"Value for {var} variable"
            }
        
        prompts.append(Prompt(
            name=template_id,
            description=template_data["description"],
            arguments=arguments_schema
        ))
    
    return prompts

@app.get_prompt()
async def handle_get_prompt(name: str, arguments: Dict[str, str]) -> str:
    """Render a prompt template with provided arguments."""
    if name not in PROMPT_TEMPLATES:
        raise ValueError(f"Unknown prompt template: {name}")
    
    template_data = PROMPT_TEMPLATES[name]
    template = template_data["template"]
    
    # Validate required variables
    missing_vars = []
    for var in template_data["variables"]:
        if var not in arguments:
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required variables: {', '.join(missing_vars)}")
    
    # Render template
    try:
        rendered = template.format(**arguments)
        return rendered
    except KeyError as e:
        raise ValueError(f"Template variable not found: {e}")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Return prompt management tools."""
    return [
        Tool(
            name="render_prompt",
            description="Render a prompt template with variables",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_id": {
                        "type": "string",
                        "enum": list(PROMPT_TEMPLATES.keys()),
                        "description": "Template identifier"
                    },
                    "variables": {
                        "type": "object",
                        "description": "Template variables as key-value pairs"
                    }
                },
                "required": ["template_id", "variables"]
            }
        ),
        Tool(
            name="create_template",
            description="Create a new prompt template",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_id": {"type": "string", "description": "Unique template ID"},
                    "name": {"type": "string", "description": "Template name"},
                    "description": {"type": "string", "description": "Template description"},
                    "template": {"type": "string", "description": "Template content with {variables}"},
                    "category": {"type": "string", "description": "Template category"}
                },
                "required": ["template_id", "name", "description", "template"]
            }
        ),
        Tool(
            name="validate_template",
            description="Validate prompt template syntax",
            inputSchema={
                "type": "object",
                "properties": {
                    "template": {"type": "string", "description": "Template content to validate"}
                },
                "required": ["template"]
            }
        ),
        Tool(
            name="list_categories",
            description="List all template categories",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute prompt template tools."""
    
    if name == "render_prompt":
        template_id = arguments["template_id"]
        variables = arguments["variables"]
        
        if template_id not in PROMPT_TEMPLATES:
            return [TextContent(
                type="text",
                text=f"Error: Unknown template '{template_id}'"
            )]
        
        template_data = PROMPT_TEMPLATES[template_id]
        
        # Validate required variables
        missing_vars = []
        for var in template_data["variables"]:
            if var not in variables:
                missing_vars.append(var)
        
        if missing_vars:
            return [TextContent(
                type="text",
                text=f"Error: Missing variables: {', '.join(missing_vars)}"
            )]
        
        try:
            rendered = template_data["template"].format(**variables)
            return [TextContent(type="text", text=rendered)]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error rendering template: {str(e)}"
            )]
    
    elif name == "create_template":
        template_id = arguments["template_id"]
        name = arguments["name"]
        description = arguments["description"]
        template = arguments["template"]
        category = arguments.get("category", "custom")
        
        if template_id in PROMPT_TEMPLATES:
            return [TextContent(
                type="text",
                text=f"Error: Template '{template_id}' already exists"
            )]
        
        # Extract variables from template
        variables = list(set(re.findall(r'\{(\w+)\}', template)))
        
        # Add to templates
        PROMPT_TEMPLATES[template_id] = {
            "name": name,
            "description": description,
            "template": template,
            "variables": variables,
            "category": category
        }
        
        result = {
            "message": f"Template '{template_id}' created successfully",
            "variables_found": variables,
            "category": category
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "validate_template":
        template = arguments["template"]
        
        # Find variables
        variables = list(set(re.findall(r'\{(\w+)\}', template)))
        
        # Test template formatting
        test_vars = {var: f"<{var}>" for var in variables}
        
        try:
            test_render = template.format(**test_vars)
            validation_result = {
                "valid": True,
                "variables": variables,
                "variable_count": len(variables),
                "preview": test_render[:200] + "..." if len(test_render) > 200 else test_render
            }
        except Exception as e:
            validation_result = {
                "valid": False,
                "error": str(e),
                "variables": variables
            }
        
        return [TextContent(
            type="text",
            text=json.dumps(validation_result, indent=2)
        )]
    
    elif name == "list_categories":
        categories = {}
        for template_id, template_data in PROMPT_TEMPLATES.items():
            category = template_data["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append({
                "id": template_id,
                "name": template_data["name"]
            })
        
        return [TextContent(
            type="text",
            text=json.dumps(categories, indent=2)
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the prompt template MCP server."""
    options = InitializationOptions(
        server_name="prompt-template-server",
        server_version="1.0.0",
        capabilities={
            "resources": {},
            "tools": {},
            "prompts": {}
        }
    )
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, options)

if __name__ == "__main__":
    asyncio.run(main())
```

This prompt template server demonstrates advanced MCP capabilities including  
the prompts interface. It provides reusable prompt templates with variable  
substitution, validation, and management tools. This pattern is valuable  
for maintaining consistent AI interactions and prompt engineering workflows.  

## Error Handling and Logging

This example demonstrates comprehensive error handling, logging, and monitoring  
patterns for production MCP servers with proper debugging capabilities.  

```python
#!/usr/bin/env python3
import asyncio
import logging
import traceback
import json
import time
from typing import Optional
from contextlib import asynccontextmanager
from mcp.server import Server
from mcp.server.models import InitializationOptions  
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/mcp-server.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("mcp-error-handling-server")

# Error tracking
error_stats = {
    "total_errors": 0,
    "error_types": {},
    "last_error": None,
    "server_start_time": time.time()
}

class MCPError(Exception):
    """Base exception for MCP server errors."""
    def __init__(self, message: str, error_code: str = "GENERAL_ERROR"):
        super().__init__(message)
        self.error_code = error_code
        self.timestamp = time.time()

class ResourceNotFoundError(MCPError):
    """Raised when a resource is not found."""
    def __init__(self, uri: str):
        super().__init__(f"Resource not found: {uri}", "RESOURCE_NOT_FOUND")
        self.uri = uri

class ValidationError(MCPError):
    """Raised when input validation fails."""
    def __init__(self, field: str, message: str):
        super().__init__(f"Validation error for {field}: {message}", "VALIDATION_ERROR")
        self.field = field

def log_error(error: Exception, context: str = ""):
    """Log error with full context and update statistics."""
    error_stats["total_errors"] += 1
    error_type = type(error).__name__
    
    if error_type not in error_stats["error_types"]:
        error_stats["error_types"][error_type] = 0
    error_stats["error_types"][error_type] += 1
    
    error_stats["last_error"] = {
        "type": error_type,
        "message": str(error),
        "context": context,
        "timestamp": time.time(),
        "traceback": traceback.format_exc()
    }
    
    logger.error(f"Error in {context}: {error}", exc_info=True)

@asynccontextmanager
async def error_handler(operation_name: str):
    """Async context manager for consistent error handling."""
    start_time = time.time()
    
    try:
        logger.info(f"Starting operation: {operation_name}")
        yield
        
        duration = time.time() - start_time
        logger.info(f"Completed operation: {operation_name} in {duration:.3f}s")
        
    except Exception as error:
        duration = time.time() - start_time
        log_error(error, f"{operation_name} (duration: {duration:.3f}s)")
        raise

app = Server("error-handling-server")

@app.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List resources with error handling."""
    async with error_handler("list_resources"):
        return [
            Resource(
                uri="test://working",
                name="Working Resource",
                description="A resource that works correctly",
                mimeType="text/plain"
            ),
            Resource(
                uri="test://error-prone",
                name="Error-Prone Resource",
                description="A resource that sometimes fails",
                mimeType="text/plain"
            ),
            Resource(
                uri="debug://logs",
                name="Server Logs",
                description="Recent server logs",
                mimeType="application/json"
            ),
            Resource(
                uri="debug://errors",
                name="Error Statistics",
                description="Server error statistics",
                mimeType="application/json"
            )
        ]

@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read resources with comprehensive error handling."""
    async with error_handler(f"read_resource:{uri}"):
        
        if uri == "test://working":
            return "This resource works perfectly!"
        
        elif uri == "test://error-prone":
            # Simulate intermittent failures
            import random
            if random.random() < 0.3:  # 30% chance of failure
                raise MCPError("Simulated intermittent failure", "INTERMITTENT_ERROR")
            return "This resource succeeded this time!"
        
        elif uri == "debug://logs":
            # Return recent log entries (mock implementation)
            logs = [
                {
                    "timestamp": time.time() - 300,
                    "level": "INFO",
                    "message": "Server started successfully"
                },
                {
                    "timestamp": time.time() - 200,
                    "level": "WARNING", 
                    "message": "High memory usage detected"
                },
                {
                    "timestamp": time.time() - 100,
                    "level": "ERROR",
                    "message": "Resource fetch failed"
                }
            ]
            return json.dumps(logs, indent=2)
        
        elif uri == "debug://errors":
            uptime = time.time() - error_stats["server_start_time"]
            error_rate = error_stats["total_errors"] / (uptime / 3600)  # errors per hour
            
            stats = {
                **error_stats,
                "uptime_hours": uptime / 3600,
                "error_rate_per_hour": error_rate
            }
            return json.dumps(stats, indent=2, default=str)
        
        else:
            raise ResourceNotFoundError(uri)

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List tools with error handling."""
    async with error_handler("list_tools"):
        return [
            Tool(
                name="validate_input",
                description="Test input validation with various scenarios",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "test_type": {
                            "type": "string",
                            "enum": ["valid", "invalid_email", "missing_field", "type_error"],
                            "description": "Type of validation test"
                        },
                        "email": {"type": "string", "description": "Email address"},
                        "age": {"type": "integer", "minimum": 0, "maximum": 150}
                    },
                    "required": ["test_type"]
                }
            ),
            Tool(
                name="simulate_error",
                description="Deliberately trigger different types of errors for testing",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "error_type": {
                            "type": "string",
                            "enum": ["timeout", "network", "database", "validation", "unexpected"],
                            "description": "Type of error to simulate"
                        },
                        "delay": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 10,
                            "description": "Delay before error (seconds)"
                        }
                    },
                    "required": ["error_type"]
                }
            ),
            Tool(
                name="get_health_check",
                description="Get comprehensive server health information",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="reset_error_stats",
                description="Reset error statistics (admin function)",
                inputSchema={"type": "object", "properties": {}}
            )
        ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute tools with robust error handling."""
    async with error_handler(f"call_tool:{name}"):
        
        if name == "validate_input":
            test_type = arguments["test_type"]
            
            try:
                if test_type == "valid":
                    email = arguments.get("email", "test@example.com")
                    age = arguments.get("age", 25)
                    
                    # Validate email format
                    import re
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    if not re.match(email_pattern, email):
                        raise ValidationError("email", "Invalid email format")
                    
                    # Validate age range
                    if not 0 <= age <= 150:
                        raise ValidationError("age", "Age must be between 0 and 150")
                    
                    return [TextContent(
                        type="text",
                        text=f"✅ Validation passed: email={email}, age={age}"
                    )]
                
                elif test_type == "invalid_email":
                    raise ValidationError("email", "Email format is invalid")
                
                elif test_type == "missing_field":
                    raise ValidationError("required_field", "Required field is missing")
                
                elif test_type == "type_error":
                    raise TypeError("Expected string but received integer")
                
            except ValidationError as e:
                return [TextContent(
                    type="text",
                    text=f"❌ Validation Error ({e.error_code}): {e.message}"
                )]
        
        elif name == "simulate_error":
            error_type = arguments["error_type"]
            delay = arguments.get("delay", 0)
            
            if delay > 0:
                await asyncio.sleep(delay)
            
            if error_type == "timeout":
                raise asyncio.TimeoutError("Operation timed out after 30 seconds")
            elif error_type == "network":
                raise ConnectionError("Network connection failed")
            elif error_type == "database":
                raise Exception("Database connection error: Unable to connect to host")
            elif error_type == "validation":
                raise ValidationError("input", "Invalid input data provided")
            elif error_type == "unexpected":
                raise RuntimeError("An unexpected error occurred during processing")
        
        elif name == "get_health_check":
            uptime = time.time() - error_stats["server_start_time"]
            
            health_info = {
                "status": "healthy",
                "uptime_seconds": uptime,
                "total_requests": 100,  # Mock value
                "error_rate": error_stats["total_errors"] / max(uptime / 3600, 1),
                "memory_usage": "45.2 MB",  # Mock value
                "last_health_check": time.time(),
                "version": "1.0.0"
            }
            
            # Determine overall health status
            if health_info["error_rate"] > 10:  # More than 10 errors per hour
                health_info["status"] = "unhealthy"
            elif health_info["error_rate"] > 5:
                health_info["status"] = "degraded"
            
            return [TextContent(
                type="text",
                text=json.dumps(health_info, indent=2)
            )]
        
        elif name == "reset_error_stats":
            global error_stats
            error_stats = {
                "total_errors": 0,
                "error_types": {},
                "last_error": None,
                "server_start_time": time.time()
            }
            
            logger.info("Error statistics reset")
            
            return [TextContent(
                type="text",
                text="✅ Error statistics have been reset"
            )]
        
        else:
            raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the error handling MCP server."""
    logger.info("🚀 Starting Error Handling MCP Server")
    
    try:
        options = InitializationOptions(
            server_name="error-handling-server",
            server_version="1.0.0",
            capabilities={
                "resources": {},
                "tools": {},
                "logging": {
                    "level": "INFO",
                    "file": "/tmp/mcp-server.log"
                }
            }
        )
        
        async with stdio_server() as (read_stream, write_stream):
            logger.info("✅ Server initialized successfully")
            await app.run(read_stream, write_stream, options)
            
    except Exception as e:
        log_error(e, "server_startup")
        logger.critical("❌ Server failed to start", exc_info=True)
        raise
    finally:
        logger.info("👋 Server shutting down")

if __name__ == "__main__":
    asyncio.run(main())
```

This error handling server demonstrates production-ready error management  
patterns including structured logging, error statistics tracking, health  
monitoring, and graceful error recovery. It provides debugging tools and  
comprehensive error reporting for maintaining robust MCP implementations.  

## Configuration Management

This example shows how to create an MCP server that manages configuration  
settings with validation, environment-based configs, and secure storage.  

```python
#!/usr/bin/env python3
import asyncio
import json
import os
import yaml
from typing import Dict, Any, Optional
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent


# Configuration storage
CONFIG_FILE = "/tmp/mcp_config.yaml"
DEFAULT_CONFIG = {
    "server": {
        "name": "MCP Configuration Server",
        "version": "1.0.0",
        "debug": False,
        "max_connections": 100
    },
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "mcp_db",
        "pool_size": 10
    },
    "cache": {
        "enabled": True,
        "ttl": 3600,
        "max_size": 1000
    },
    "logging": {
        "level": "INFO",
        "file": "/tmp/mcp.log",
        "rotate": True
    }
}

def load_config() -> Dict[str, Any]:
    """Load configuration from file or create default."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return yaml.safe_load(f) or DEFAULT_CONFIG
        except Exception:
            return DEFAULT_CONFIG
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    with open(CONFIG_FILE, 'w') as f:
        yaml.safe_dump(config, f, default_flow_style=False, indent=2)

def validate_config(config: Dict[str, Any]) -> list[str]:
    """Validate configuration values."""
    errors = []
    
    # Validate server config
    if "server" in config:
        server_config = config["server"]
        if "max_connections" in server_config:
            if not isinstance(server_config["max_connections"], int) or server_config["max_connections"] < 1:
                errors.append("server.max_connections must be a positive integer")
    
    # Validate database config
    if "database" in config:
        db_config = config["database"]
        if "port" in db_config:
            if not isinstance(db_config["port"], int) or not (1 <= db_config["port"] <= 65535):
                errors.append("database.port must be between 1 and 65535")
    
    # Validate cache config
    if "cache" in config:
        cache_config = config["cache"]
        if "ttl" in cache_config:
            if not isinstance(cache_config["ttl"], int) or cache_config["ttl"] < 0:
                errors.append("cache.ttl must be a non-negative integer")
    
    return errors

app = Server("config-management-server")

@app.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List configuration resources."""
    return [
        Resource(
            uri="config://current",
            name="Current Configuration",
            description="Currently active configuration",
            mimeType="application/yaml"
        ),
        Resource(
            uri="config://default",
            name="Default Configuration",
            description="Default configuration template",
            mimeType="application/yaml"
        ),
        Resource(
            uri="config://environment",
            name="Environment Variables",
            description="Relevant environment variables",
            mimeType="application/json"
        )
    ]

@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read configuration resources."""
    if uri == "config://current":
        config = load_config()
        return yaml.dump(config, default_flow_style=False, indent=2)
    
    elif uri == "config://default":
        return yaml.dump(DEFAULT_CONFIG, default_flow_style=False, indent=2)
    
    elif uri == "config://environment":
        env_vars = {
            "MCP_DEBUG": os.getenv("MCP_DEBUG", "false"),
            "MCP_LOG_LEVEL": os.getenv("MCP_LOG_LEVEL", "INFO"),
            "DATABASE_URL": os.getenv("DATABASE_URL", "not set"),
            "REDIS_URL": os.getenv("REDIS_URL", "not set"),
            "API_KEY": "***" if os.getenv("API_KEY") else "not set"
        }
        return json.dumps(env_vars, indent=2)
    
    else:
        raise ValueError(f"Unknown resource: {uri}")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Return configuration management tools."""
    return [
        Tool(
            name="get_config_value",
            description="Get a specific configuration value",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Configuration key (dot notation, e.g., 'server.port')"
                    }
                },
                "required": ["key"]
            }
        ),
        Tool(
            name="set_config_value",
            description="Set a configuration value",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Configuration key"},
                    "value": {"description": "Configuration value"},
                    "validate": {"type": "boolean", "default": True}
                },
                "required": ["key", "value"]
            }
        ),
        Tool(
            name="validate_config",
            description="Validate current configuration",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="reset_config",
            description="Reset configuration to defaults",
            inputSchema={
                "type": "object",
                "properties": {
                    "section": {
                        "type": "string",
                        "description": "Optional: reset only specific section"
                    }
                }
            }
        ),
        Tool(
            name="backup_config",
            description="Create configuration backup",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute configuration tools."""
    
    if name == "get_config_value":
        key = arguments["key"]
        config = load_config()
        
        # Navigate nested configuration using dot notation
        try:
            value = config
            for part in key.split('.'):
                value = value[part]
            
            result = {
                "key": key,
                "value": value,
                "type": type(value).__name__
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except (KeyError, TypeError):
            return [TextContent(
                type="text",
                text=f"Configuration key '{key}' not found"
            )]
    
    elif name == "set_config_value":
        key = arguments["key"]
        value = arguments["value"]
        validate = arguments.get("validate", True)
        
        config = load_config()
        
        # Navigate to parent and set value
        try:
            target = config
            parts = key.split('.')
            
            # Navigate to parent
            for part in parts[:-1]:
                if part not in target:
                    target[part] = {}
                target = target[part]
            
            # Set the value
            target[parts[-1]] = value
            
            # Validate if requested
            if validate:
                errors = validate_config(config)
                if errors:
                    return [TextContent(
                        type="text",
                        text=f"Validation failed:\n" + "\n".join(f"- {error}" for error in errors)
                    )]
            
            # Save configuration
            save_config(config)
            
            return [TextContent(
                type="text",
                text=f"✅ Configuration updated: {key} = {value}"
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error updating configuration: {str(e)}"
            )]
    
    elif name == "validate_config":
        config = load_config()
        errors = validate_config(config)
        
        if errors:
            result = {
                "valid": False,
                "errors": errors
            }
        else:
            result = {
                "valid": True,
                "message": "Configuration is valid"
            }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "reset_config":
        section = arguments.get("section")
        
        if section:
            # Reset only specific section
            config = load_config()
            if section in DEFAULT_CONFIG:
                config[section] = DEFAULT_CONFIG[section].copy()
                save_config(config)
                message = f"✅ Section '{section}' reset to defaults"
            else:
                message = f"❌ Section '{section}' not found in default configuration"
        else:
            # Reset entire configuration
            save_config(DEFAULT_CONFIG.copy())
            message = "✅ Configuration reset to defaults"
        
        return [TextContent(type="text", text=message)]
    
    elif name == "backup_config":
        import datetime
        
        config = load_config()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"/tmp/mcp_config_backup_{timestamp}.yaml"
        
        try:
            with open(backup_file, 'w') as f:
                yaml.safe_dump(config, f, default_flow_style=False, indent=2)
            
            result = {
                "backup_created": backup_file,
                "timestamp": timestamp,
                "size": os.path.getsize(backup_file)
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error creating backup: {str(e)}"
            )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the configuration management MCP server."""
    # Ensure configuration file exists
    config = load_config()
    
    options = InitializationOptions(
        server_name="config-management-server",
        server_version="1.0.0",
        capabilities={
            "resources": {},
            "tools": {}
        }
    )
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, options)

if __name__ == "__main__":
    asyncio.run(main())
```

This configuration management server demonstrates handling structured  
configuration with validation, backup/restore capabilities, and environment  
variable integration. It provides a systematic approach to managing  
application settings through MCP.  

## Data Processing Pipeline

This example creates an MCP server that manages data processing pipelines  
with transformation steps, filtering, and batch operations.  

```python
#!/usr/bin/env python3
import asyncio
import json
import csv
import io
import statistics
from typing import List, Dict, Any, Callable
from dataclasses import dataclass
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent


@dataclass
class DataRecord:
    """Represents a single data record."""
    id: str
    data: Dict[str, Any]

class DataPipeline:
    """Data processing pipeline with transformation steps."""
    
    def __init__(self, name: str):
        self.name = name
        self.steps: List[Callable] = []
        self.data: List[DataRecord] = []
    
    def add_step(self, step: Callable):
        """Add a processing step to the pipeline."""
        self.steps.append(step)
    
    async def process(self, data: List[DataRecord]) -> List[DataRecord]:
        """Execute all pipeline steps on data."""
        result = data.copy()
        
        for step in self.steps:
            result = await step(result)
        
        return result

# Sample data
SAMPLE_DATA = [
    DataRecord("1", {"name": "Alice", "age": 25, "score": 85, "department": "Engineering"}),
    DataRecord("2", {"name": "Bob", "age": 30, "score": 92, "department": "Marketing"}),
    DataRecord("3", {"name": "Carol", "age": 28, "score": 78, "department": "Engineering"}),
    DataRecord("4", {"name": "David", "age": 35, "score": 88, "department": "Sales"}),
    DataRecord("5", {"name": "Eve", "age": 26, "score": 95, "department": "Engineering"}),
]

# Pipeline storage
pipelines: Dict[str, DataPipeline] = {}

app = Server("data-processing-server")

# Processing functions
async def filter_by_age(data: List[DataRecord], min_age: int = 25, max_age: int = 65) -> List[DataRecord]:
    """Filter records by age range."""
    return [record for record in data 
            if min_age <= record.data.get("age", 0) <= max_age]

async def filter_by_department(data: List[DataRecord], departments: List[str]) -> List[DataRecord]:
    """Filter records by department."""
    return [record for record in data 
            if record.data.get("department") in departments]

async def transform_names(data: List[DataRecord]) -> List[DataRecord]:
    """Transform names to uppercase."""
    for record in data:
        if "name" in record.data:
            record.data["name"] = record.data["name"].upper()
    return data

async def add_score_category(data: List[DataRecord]) -> List[DataRecord]:
    """Add score category based on score."""
    for record in data:
        score = record.data.get("score", 0)
        if score >= 90:
            category = "Excellent"
        elif score >= 80:
            category = "Good"
        elif score >= 70:
            category = "Fair"
        else:
            category = "Poor"
        
        record.data["score_category"] = category
    
    return data

async def calculate_statistics(data: List[DataRecord]) -> Dict[str, Any]:
    """Calculate statistics for numerical fields."""
    if not data:
        return {}
    
    # Extract numerical fields
    ages = [r.data.get("age", 0) for r in data if "age" in r.data]
    scores = [r.data.get("score", 0) for r in data if "score" in r.data]
    
    stats = {
        "count": len(data),
        "departments": list(set(r.data.get("department") for r in data if "department" in r.data))
    }
    
    if ages:
        stats["age_stats"] = {
            "mean": statistics.mean(ages),
            "median": statistics.median(ages),
            "min": min(ages),
            "max": max(ages)
        }
    
    if scores:
        stats["score_stats"] = {
            "mean": statistics.mean(scores),
            "median": statistics.median(scores),
            "min": min(scores),
            "max": max(scores)
        }
    
    return stats

@app.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List data processing resources."""
    resources = [
        Resource(
            uri="data://sample",
            name="Sample Dataset",
            description="Sample employee data for processing",
            mimeType="application/json"
        ),
        Resource(
            uri="data://pipelines",
            name="Processing Pipelines",
            description="Available data processing pipelines",
            mimeType="application/json"
        )
    ]
    
    # Add individual pipeline resources
    for pipeline_name in pipelines:
        resources.append(Resource(
            uri=f"pipeline://{pipeline_name}",
            name=f"Pipeline: {pipeline_name}",
            description=f"Data processing pipeline: {pipeline_name}",
            mimeType="application/json"
        ))
    
    return resources

@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read data processing resources."""
    if uri == "data://sample":
        data_dict = [
            {"id": record.id, **record.data} 
            for record in SAMPLE_DATA
        ]
        return json.dumps(data_dict, indent=2)
    
    elif uri == "data://pipelines":
        pipeline_info = {}
        for name, pipeline in pipelines.items():
            pipeline_info[name] = {
                "name": pipeline.name,
                "steps": len(pipeline.steps),
                "data_count": len(pipeline.data)
            }
        return json.dumps(pipeline_info, indent=2)
    
    elif uri.startswith("pipeline://"):
        pipeline_name = uri.replace("pipeline://", "")
        if pipeline_name in pipelines:
            pipeline = pipelines[pipeline_name]
            pipeline_data = [
                {"id": record.id, **record.data}
                for record in pipeline.data
            ]
            return json.dumps(pipeline_data, indent=2)
        else:
            raise ValueError(f"Pipeline not found: {pipeline_name}")
    
    else:
        raise ValueError(f"Unknown resource: {uri}")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Return data processing tools."""
    return [
        Tool(
            name="create_pipeline",
            description="Create a new data processing pipeline",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Pipeline name"},
                    "description": {"type": "string", "description": "Pipeline description"}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="add_filter_step",
            description="Add filtering step to pipeline",
            inputSchema={
                "type": "object",
                "properties": {
                    "pipeline": {"type": "string", "description": "Pipeline name"},
                    "filter_type": {
                        "type": "string",
                        "enum": ["age", "department", "score"],
                        "description": "Type of filter"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Filter parameters"
                    }
                },
                "required": ["pipeline", "filter_type"]
            }
        ),
        Tool(
            name="add_transform_step",
            description="Add transformation step to pipeline",
            inputSchema={
                "type": "object",
                "properties": {
                    "pipeline": {"type": "string", "description": "Pipeline name"},
                    "transform_type": {
                        "type": "string",
                        "enum": ["uppercase_names", "add_score_category"],
                        "description": "Type of transformation"
                    }
                },
                "required": ["pipeline", "transform_type"]
            }
        ),
        Tool(
            name="run_pipeline",
            description="Execute a data processing pipeline",
            inputSchema={
                "type": "object",
                "properties": {
                    "pipeline": {"type": "string", "description": "Pipeline name"},
                    "data_source": {
                        "type": "string",
                        "enum": ["sample", "custom"],
                        "default": "sample",
                        "description": "Data source to process"
                    }
                },
                "required": ["pipeline"]
            }
        ),
        Tool(
            name="export_data",
            description="Export processed data in various formats",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {"type": "string", "description": "Data source (pipeline name or 'sample')"},
                    "format": {
                        "type": "string",
                        "enum": ["json", "csv"],
                        "default": "json",
                        "description": "Export format"
                    }
                },
                "required": ["source"]
            }
        ),
        Tool(
            name="calculate_stats",
            description="Calculate statistics for a data source",
            inputSchema={
                "type": "object", 
                "properties": {
                    "source": {"type": "string", "description": "Data source"}
                },
                "required": ["source"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute data processing tools."""
    
    if name == "create_pipeline":
        pipeline_name = arguments["name"]
        description = arguments.get("description", "")
        
        if pipeline_name in pipelines:
            return [TextContent(
                type="text",
                text=f"Pipeline '{pipeline_name}' already exists"
            )]
        
        pipelines[pipeline_name] = DataPipeline(pipeline_name)
        
        result = {
            "message": f"Pipeline '{pipeline_name}' created successfully",
            "description": description
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "add_filter_step":
        pipeline_name = arguments["pipeline"]
        filter_type = arguments["filter_type"]
        parameters = arguments.get("parameters", {})
        
        if pipeline_name not in pipelines:
            return [TextContent(
                type="text",
                text=f"Pipeline '{pipeline_name}' not found"
            )]
        
        pipeline = pipelines[pipeline_name]
        
        if filter_type == "age":
            min_age = parameters.get("min_age", 25)
            max_age = parameters.get("max_age", 65)
            step = lambda data: filter_by_age(data, min_age, max_age)
        elif filter_type == "department":
            departments = parameters.get("departments", ["Engineering"])
            step = lambda data: filter_by_department(data, departments)
        elif filter_type == "score":
            min_score = parameters.get("min_score", 0)
            step = lambda data: [r for r in data if r.data.get("score", 0) >= min_score]
        else:
            return [TextContent(
                type="text",
                text=f"Unknown filter type: {filter_type}"
            )]
        
        pipeline.add_step(step)
        
        return [TextContent(
            type="text",
            text=f"Filter step '{filter_type}' added to pipeline '{pipeline_name}'"
        )]
    
    elif name == "add_transform_step":
        pipeline_name = arguments["pipeline"]
        transform_type = arguments["transform_type"]
        
        if pipeline_name not in pipelines:
            return [TextContent(
                type="text",
                text=f"Pipeline '{pipeline_name}' not found"
            )]
        
        pipeline = pipelines[pipeline_name]
        
        if transform_type == "uppercase_names":
            step = transform_names
        elif transform_type == "add_score_category":
            step = add_score_category
        else:
            return [TextContent(
                type="text",
                text=f"Unknown transform type: {transform_type}"
            )]
        
        pipeline.add_step(step)
        
        return [TextContent(
            type="text",
            text=f"Transform step '{transform_type}' added to pipeline '{pipeline_name}'"
        )]
    
    elif name == "run_pipeline":
        pipeline_name = arguments["pipeline"]
        data_source = arguments.get("data_source", "sample")
        
        if pipeline_name not in pipelines:
            return [TextContent(
                type="text",
                text=f"Pipeline '{pipeline_name}' not found"
            )]
        
        pipeline = pipelines[pipeline_name]
        
        # Get source data
        if data_source == "sample":
            source_data = SAMPLE_DATA.copy()
        else:
            return [TextContent(
                type="text",
                text=f"Unknown data source: {data_source}"
            )]
        
        # Process data through pipeline
        processed_data = await pipeline.process(source_data)
        pipeline.data = processed_data
        
        result = {
            "pipeline": pipeline_name,
            "input_records": len(source_data),
            "output_records": len(processed_data),
            "steps_executed": len(pipeline.steps)
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "export_data":
        source = arguments["source"]
        format_type = arguments.get("format", "json")
        
        # Get data
        if source == "sample":
            data = SAMPLE_DATA
        elif source in pipelines:
            data = pipelines[source].data
        else:
            return [TextContent(
                type="text",
                text=f"Data source '{source}' not found"
            )]
        
        if format_type == "json":
            export_data = [
                {"id": record.id, **record.data}
                for record in data
            ]
            output = json.dumps(export_data, indent=2)
        
        elif format_type == "csv":
            if not data:
                output = ""
            else:
                # Get all possible fields
                fieldnames = set()
                for record in data:
                    fieldnames.update(["id"] + list(record.data.keys()))
                
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=sorted(fieldnames))
                writer.writeheader()
                
                for record in data:
                    row = {"id": record.id, **record.data}
                    writer.writerow(row)
                
                output = output.getvalue()
        
        else:
            return [TextContent(
                type="text",
                text=f"Unsupported format: {format_type}"
            )]
        
        return [TextContent(type="text", text=output)]
    
    elif name == "calculate_stats":
        source = arguments["source"]
        
        # Get data
        if source == "sample":
            data = SAMPLE_DATA
        elif source in pipelines:
            data = pipelines[source].data
        else:
            return [TextContent(
                type="text",
                text=f"Data source '{source}' not found"
            )]
        
        stats = await calculate_statistics(data)
        
        return [TextContent(
            type="text",
            text=json.dumps(stats, indent=2)
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the data processing MCP server."""
    options = InitializationOptions(
        server_name="data-processing-server",
        server_version="1.0.0",
        capabilities={
            "resources": {},
            "tools": {}
        }
    )
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, options)

if __name__ == "__main__":
    asyncio.run(main())
```

This data processing server demonstrates building complex data pipelines  
with multiple processing steps. It shows filtering, transformation, and  
statistical operations while maintaining data lineage and providing  
export capabilities in multiple formats.  

## Monitoring and Metrics

This example creates an MCP server for system monitoring with metrics  
collection, alerting, and performance tracking capabilities.  

```python
#!/usr/bin/env python3
import asyncio
import psutil
import json
import time
from typing import Dict, List, Any
from dataclasses import dataclass
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent


@dataclass
class MetricSample:
    """Single metric sample with timestamp."""
    timestamp: float
    value: float
    tags: Dict[str, str]

@dataclass
class Alert:
    """Alert configuration."""
    name: str
    metric: str
    threshold: float
    condition: str  # "gt", "lt", "eq"
    enabled: bool = True

# Metrics storage
metrics_history: Dict[str, List[MetricSample]] = {}
alerts: Dict[str, Alert] = {}
alert_history: List[Dict[str, Any]] = []

def collect_system_metrics() -> Dict[str, float]:
    """Collect current system metrics."""
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "load_average": psutil.getloadavg()[0],
        "process_count": len(psutil.pids())
    }

def store_metric(name: str, value: float, tags: Dict[str, str] = None):
    """Store a metric sample."""
    if name not in metrics_history:
        metrics_history[name] = []
    
    sample = MetricSample(
        timestamp=time.time(),
        value=value,
        tags=tags or {}
    )
    
    metrics_history[name].append(sample)
    
    # Keep only last 1000 samples
    if len(metrics_history[name]) > 1000:
        metrics_history[name] = metrics_history[name][-1000:]
    
    # Check alerts
    check_alerts(name, value)

def check_alerts(metric_name: str, value: float):
    """Check if any alerts should be triggered."""
    for alert_name, alert in alerts.items():
        if alert.metric == metric_name and alert.enabled:
            triggered = False
            
            if alert.condition == "gt" and value > alert.threshold:
                triggered = True
            elif alert.condition == "lt" and value < alert.threshold:
                triggered = True
            elif alert.condition == "eq" and value == alert.threshold:
                triggered = True
            
            if triggered:
                alert_event = {
                    "alert": alert_name,
                    "metric": metric_name,
                    "value": value,
                    "threshold": alert.threshold,
                    "condition": alert.condition,
                    "timestamp": time.time()
                }
                alert_history.append(alert_event)
                
                # Keep only last 100 alerts
                if len(alert_history) > 100:
                    alert_history[:] = alert_history[-100:]

app = Server("monitoring-metrics-server")

@app.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List monitoring resources."""
    resources = [
        Resource(
            uri="metrics://current",
            name="Current Metrics",
            description="Current system metrics snapshot",
            mimeType="application/json"
        ),
        Resource(
            uri="metrics://history",
            name="Metrics History",
            description="Historical metrics data",
            mimeType="application/json"
        ),
        Resource(
            uri="alerts://active",
            name="Active Alerts",
            description="Currently configured alerts",
            mimeType="application/json"
        ),
        Resource(
            uri="alerts://history",
            name="Alert History",
            description="Recent alert events",
            mimeType="application/json"
        )
    ]
    
    return resources

@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read monitoring resources."""
    if uri == "metrics://current":
        current_metrics = collect_system_metrics()
        
        # Add timestamp
        result = {
            "timestamp": time.time(),
            "metrics": current_metrics
        }
        
        # Store the metrics
        for name, value in current_metrics.items():
            store_metric(name, value, {"source": "system"})
        
        return json.dumps(result, indent=2)
    
    elif uri == "metrics://history":
        # Return recent history for all metrics
        history_data = {}
        for metric_name, samples in metrics_history.items():
            # Get last 50 samples
            recent_samples = samples[-50:]
            history_data[metric_name] = [
                {
                    "timestamp": sample.timestamp,
                    "value": sample.value,
                    "tags": sample.tags
                }
                for sample in recent_samples
            ]
        
        return json.dumps(history_data, indent=2)
    
    elif uri == "alerts://active":
        alert_data = {}
        for name, alert in alerts.items():
            alert_data[name] = {
                "metric": alert.metric,
                "threshold": alert.threshold,
                "condition": alert.condition,
                "enabled": alert.enabled
            }
        
        return json.dumps(alert_data, indent=2)
    
    elif uri == "alerts://history":
        return json.dumps(alert_history[-20:], indent=2)  # Last 20 alerts
    
    else:
        raise ValueError(f"Unknown resource: {uri}")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Return monitoring and metrics tools."""
    return [
        Tool(
            name="collect_metrics",
            description="Collect and store current system metrics",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_metric_stats",
            description="Get statistics for a specific metric",
            inputSchema={
                "type": "object",
                "properties": {
                    "metric": {"type": "string", "description": "Metric name"},
                    "duration": {
                        "type": "integer",
                        "default": 3600,
                        "description": "Duration in seconds to analyze"
                    }
                },
                "required": ["metric"]
            }
        ),
        Tool(
            name="create_alert",
            description="Create a new alert",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Alert name"},
                    "metric": {"type": "string", "description": "Metric to monitor"},
                    "threshold": {"type": "number", "description": "Alert threshold"},
                    "condition": {
                        "type": "string",
                        "enum": ["gt", "lt", "eq"],
                        "description": "Alert condition (gt=greater than, lt=less than, eq=equals)"
                    }
                },
                "required": ["name", "metric", "threshold", "condition"]
            }
        ),
        Tool(
            name="update_alert",
            description="Update an existing alert",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Alert name"},
                    "threshold": {"type": "number", "description": "New threshold"},
                    "enabled": {"type": "boolean", "description": "Enable/disable alert"}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="get_system_info",
            description="Get comprehensive system information",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute monitoring tools."""
    
    if name == "collect_metrics":
        metrics = collect_system_metrics()
        
        # Store all metrics
        for metric_name, value in metrics.items():
            store_metric(metric_name, value, {"source": "manual"})
        
        result = {
            "collected_at": time.time(),
            "metrics": metrics,
            "stored": True
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "get_metric_stats":
        metric_name = arguments["metric"]
        duration = arguments.get("duration", 3600)
        
        if metric_name not in metrics_history:
            return [TextContent(
                type="text",
                text=f"Metric '{metric_name}' not found"
            )]
        
        # Filter samples by duration
        cutoff_time = time.time() - duration
        recent_samples = [
            sample for sample in metrics_history[metric_name]
            if sample.timestamp >= cutoff_time
        ]
        
        if not recent_samples:
            return [TextContent(
                type="text",
                text=f"No recent data for metric '{metric_name}'"
            )]
        
        values = [sample.value for sample in recent_samples]
        
        stats = {
            "metric": metric_name,
            "duration_seconds": duration,
            "sample_count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1],
            "first": values[0],
            "change": values[-1] - values[0] if len(values) > 1 else 0
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(stats, indent=2)
        )]
    
    elif name == "create_alert":
        alert_name = arguments["name"]
        metric = arguments["metric"]
        threshold = arguments["threshold"]
        condition = arguments["condition"]
        
        if alert_name in alerts:
            return [TextContent(
                type="text",
                text=f"Alert '{alert_name}' already exists"
            )]
        
        alerts[alert_name] = Alert(
            name=alert_name,
            metric=metric,
            threshold=threshold,
            condition=condition
        )
        
        result = {
            "message": f"Alert '{alert_name}' created successfully",
            "alert": {
                "metric": metric,
                "threshold": threshold,
                "condition": condition,
                "enabled": True
            }
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "update_alert":
        alert_name = arguments["name"]
        
        if alert_name not in alerts:
            return [TextContent(
                type="text",
                text=f"Alert '{alert_name}' not found"
            )]
        
        alert = alerts[alert_name]
        
        if "threshold" in arguments:
            alert.threshold = arguments["threshold"]
        
        if "enabled" in arguments:
            alert.enabled = arguments["enabled"]
        
        result = {
            "message": f"Alert '{alert_name}' updated successfully",
            "alert": {
                "metric": alert.metric,
                "threshold": alert.threshold,
                "condition": alert.condition,
                "enabled": alert.enabled
            }
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "get_system_info":
        info = {
            "system": {
                "platform": psutil.LINUX if hasattr(psutil, 'LINUX') else "unknown",
                "boot_time": psutil.boot_time(),
                "uptime": time.time() - psutil.boot_time()
            },
            "cpu": {
                "count": psutil.cpu_count(),
                "count_logical": psutil.cpu_count(logical=True),
                "current_freq": psutil.cpu_freq().current if psutil.cpu_freq() else None
            },
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "used": psutil.virtual_memory().used
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "free": psutil.disk_usage('/').free,
                "used": psutil.disk_usage('/').used
            },
            "network": {
                "interfaces": list(psutil.net_if_addrs().keys())
            }
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(info, indent=2, default=str)
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def metric_collector():
    """Background task to collect metrics periodically."""
    while True:
        try:
            metrics = collect_system_metrics()
            for name, value in metrics.items():
                store_metric(name, value, {"source": "background"})
            
            await asyncio.sleep(60)  # Collect every minute
        except Exception as e:
            print(f"Error collecting metrics: {e}")
            await asyncio.sleep(10)

async def main():
    """Run the monitoring MCP server."""
    # Start background metric collection
    asyncio.create_task(metric_collector())
    
    options = InitializationOptions(
        server_name="monitoring-metrics-server",
        server_version="1.0.0",
        capabilities={
            "resources": {},
            "tools": {}
        }
    )
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, options)

if __name__ == "__main__":
    asyncio.run(main())
```

This monitoring server demonstrates comprehensive system metrics collection  
with alerting capabilities. It provides real-time system monitoring,  
historical data analysis, and configurable alert thresholds with  
background metric collection tasks.  

## Task Queue Management

This example shows how to create an MCP server that manages background  
tasks with queuing, scheduling, and status tracking capabilities.  

```python
#!/usr/bin/env python3
import asyncio
import json
import time
import uuid
from enum import Enum
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Task:
    """Represents a background task."""
    id: str
    name: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Any = None
    error: Optional[str] = None
    progress: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

# Task storage and queue
tasks: Dict[str, Task] = {}
task_queue = asyncio.Queue()
worker_count = 3
workers_running = False

# Task handlers registry
task_handlers: Dict[str, Callable] = {}

def register_task_handler(name: str):
    """Decorator to register task handlers."""
    def decorator(func):
        task_handlers[name] = func
        return func
    return decorator

@register_task_handler("sleep_task")
async def sleep_task_handler(task: Task, **kwargs):
    """Handler for sleep task - simulates long-running work."""
    duration = kwargs.get("duration", 5)
    steps = 10
    
    for i in range(steps):
        if task.status == TaskStatus.CANCELLED:
            return
        
        task.progress = (i + 1) / steps
        await asyncio.sleep(duration / steps)
    
    return f"Slept for {duration} seconds"

@register_task_handler("data_processing")
async def data_processing_handler(task: Task, **kwargs):
    """Handler for data processing task."""
    data = kwargs.get("data", [])
    operation = kwargs.get("operation", "sum")
    
    if operation == "sum":
        result = sum(data) if data else 0
    elif operation == "average":
        result = sum(data) / len(data) if data else 0
    elif operation == "max":
        result = max(data) if data else 0
    elif operation == "min":
        result = min(data) if data else 0
    else:
        raise ValueError(f"Unknown operation: {operation}")
    
    # Simulate processing time
    await asyncio.sleep(2)
    task.progress = 1.0
    
    return {"operation": operation, "result": result, "data_size": len(data)}

@register_task_handler("file_processing")
async def file_processing_handler(task: Task, **kwargs):
    """Handler for file processing task."""
    filename = kwargs.get("filename", "test.txt")
    action = kwargs.get("action", "analyze")
    
    # Simulate file processing
    steps = ["reading", "parsing", "analyzing", "finalizing"]
    
    for i, step in enumerate(steps):
        if task.status == TaskStatus.CANCELLED:
            return
        
        task.metadata["current_step"] = step
        task.progress = (i + 1) / len(steps)
        await asyncio.sleep(1)
    
    return {
        "filename": filename,
        "action": action,
        "lines_processed": 100,
        "size_bytes": 2048
    }

async def task_worker(worker_id: int):
    """Background worker to process tasks."""
    print(f"Worker {worker_id} started")
    
    while workers_running:
        try:
            # Get task from queue with timeout
            try:
                task_id = await asyncio.wait_for(task_queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            
            task = tasks.get(task_id)
            if not task or task.status != TaskStatus.PENDING:
                continue
            
            # Start task execution
            task.status = TaskStatus.RUNNING
            task.started_at = time.time()
            
            print(f"Worker {worker_id} processing task {task_id}: {task.name}")
            
            try:
                # Get task handler
                handler = task_handlers.get(task.name)
                if not handler:
                    raise ValueError(f"No handler found for task: {task.name}")
                
                # Execute task
                result = await handler(task, **task.metadata)
                
                # Mark as completed
                task.status = TaskStatus.COMPLETED
                task.completed_at = time.time()
                task.result = result
                task.progress = 1.0
                
                print(f"Worker {worker_id} completed task {task_id}")
                
            except Exception as e:
                # Mark as failed
                task.status = TaskStatus.FAILED
                task.completed_at = time.time()
                task.error = str(e)
                
                print(f"Worker {worker_id} failed task {task_id}: {e}")
            
            finally:
                task_queue.task_done()
                
        except Exception as e:
            print(f"Worker {worker_id} error: {e}")
            await asyncio.sleep(1)
    
    print(f"Worker {worker_id} stopped")

app = Server("task-queue-server")

@app.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List task queue resources."""
    return [
        Resource(
            uri="queue://status",
            name="Queue Status",
            description="Current queue status and statistics",
            mimeType="application/json"
        ),
        Resource(
            uri="tasks://all",
            name="All Tasks",
            description="List of all tasks",
            mimeType="application/json"
        ),
        Resource(
            uri="tasks://running",
            name="Running Tasks",
            description="Currently running tasks",
            mimeType="application/json"
        ),
        Resource(
            uri="workers://status",
            name="Worker Status",
            description="Status of background workers",
            mimeType="application/json"
        )
    ]

@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read task queue resources."""
    if uri == "queue://status":
        queue_info = {
            "queue_size": task_queue.qsize(),
            "total_tasks": len(tasks),
            "pending_tasks": len([t for t in tasks.values() if t.status == TaskStatus.PENDING]),
            "running_tasks": len([t for t in tasks.values() if t.status == TaskStatus.RUNNING]),
            "completed_tasks": len([t for t in tasks.values() if t.status == TaskStatus.COMPLETED]),
            "failed_tasks": len([t for t in tasks.values() if t.status == TaskStatus.FAILED]),
            "workers_running": workers_running,
            "worker_count": worker_count
        }
        return json.dumps(queue_info, indent=2)
    
    elif uri == "tasks://all":
        task_list = []
        for task in tasks.values():
            task_info = {
                "id": task.id,
                "name": task.name,
                "status": task.status.value,
                "created_at": task.created_at,
                "started_at": task.started_at,
                "completed_at": task.completed_at,
                "progress": task.progress,
                "duration": (task.completed_at or time.time()) - task.created_at if task.started_at else None
            }
            task_list.append(task_info)
        
        return json.dumps(sorted(task_list, key=lambda x: x["created_at"], reverse=True), indent=2)
    
    elif uri == "tasks://running":
        running_tasks = [
            {
                "id": task.id,
                "name": task.name,
                "progress": task.progress,
                "started_at": task.started_at,
                "duration": time.time() - task.started_at,
                "metadata": task.metadata
            }
            for task in tasks.values()
            if task.status == TaskStatus.RUNNING
        ]
        return json.dumps(running_tasks, indent=2)
    
    elif uri == "workers://status":
        worker_info = {
            "workers_running": workers_running,
            "worker_count": worker_count,
            "available_handlers": list(task_handlers.keys())
        }
        return json.dumps(worker_info, indent=2)
    
    else:
        raise ValueError(f"Unknown resource: {uri}")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Return task management tools."""
    return [
        Tool(
            name="create_task",
            description="Create and enqueue a new task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_type": {
                        "type": "string",
                        "enum": list(task_handlers.keys()),
                        "description": "Type of task to create"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Task parameters"
                    }
                },
                "required": ["task_type"]
            }
        ),
        Tool(
            name="get_task",
            description="Get details of a specific task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID"}
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="cancel_task",
            description="Cancel a pending or running task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID"}
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="start_workers",
            description="Start background task workers",
            inputSchema={
                "type": "object",
                "properties": {
                    "count": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 10,
                        "default": 3,
                        "description": "Number of workers to start"
                    }
                }
            }
        ),
        Tool(
            name="stop_workers",
            description="Stop background task workers",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="clear_completed",
            description="Clear completed and failed tasks",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute task management tools."""
    
    if name == "create_task":
        task_type = arguments["task_type"]
        parameters = arguments.get("parameters", {})
        
        if task_type not in task_handlers:
            return [TextContent(
                type="text",
                text=f"Unknown task type: {task_type}"
            )]
        
        # Create task
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            name=task_type,
            metadata=parameters
        )
        
        tasks[task_id] = task
        
        # Add to queue
        await task_queue.put(task_id)
        
        result = {
            "task_id": task_id,
            "task_type": task_type,
            "status": task.status.value,
            "created_at": task.created_at,
            "queue_position": task_queue.qsize()
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "get_task":
        task_id = arguments["task_id"]
        
        if task_id not in tasks:
            return [TextContent(
                type="text",
                text=f"Task not found: {task_id}"
            )]
        
        task = tasks[task_id]
        
        task_info = {
            "id": task.id,
            "name": task.name,
            "status": task.status.value,
            "progress": task.progress,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "result": task.result,
            "error": task.error,
            "metadata": task.metadata
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(task_info, indent=2)
        )]
    
    elif name == "cancel_task":
        task_id = arguments["task_id"]
        
        if task_id not in tasks:
            return [TextContent(
                type="text",
                text=f"Task not found: {task_id}"
            )]
        
        task = tasks[task_id]
        
        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            return [TextContent(
                type="text",
                text=f"Cannot cancel task in status: {task.status.value}"
            )]
        
        task.status = TaskStatus.CANCELLED
        task.completed_at = time.time()
        
        return [TextContent(
            type="text",
            text=f"Task {task_id} cancelled successfully"
        )]
    
    elif name == "start_workers":
        global workers_running, worker_count
        
        count = arguments.get("count", 3)
        
        if workers_running:
            return [TextContent(
                type="text",
                text="Workers are already running"
            )]
        
        workers_running = True
        worker_count = count
        
        # Start worker tasks
        for i in range(count):
            asyncio.create_task(task_worker(i + 1))
        
        return [TextContent(
            type="text",
            text=f"Started {count} workers successfully"
        )]
    
    elif name == "stop_workers":
        global workers_running
        
        if not workers_running:
            return [TextContent(
                type="text",
                text="Workers are not running"
            )]
        
        workers_running = False
        
        return [TextContent(
            type="text",
            text="Workers stopped successfully"
        )]
    
    elif name == "clear_completed":
        completed_statuses = [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
        
        cleared_count = 0
        task_ids_to_remove = []
        
        for task_id, task in tasks.items():
            if task.status in completed_statuses:
                task_ids_to_remove.append(task_id)
                cleared_count += 1
        
        for task_id in task_ids_to_remove:
            del tasks[task_id]
        
        return [TextContent(
            type="text",
            text=f"Cleared {cleared_count} completed tasks"
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the task queue MCP server."""
    options = InitializationOptions(
        server_name="task-queue-server",
        server_version="1.0.0",
        capabilities={
            "resources": {},
            "tools": {}
        }
    )
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, options)

if __name__ == "__main__":
    asyncio.run(main())
```

This task queue server demonstrates advanced background processing with  
worker pools, task lifecycle management, and progress tracking. It provides  
a robust foundation for building distributed task processing systems  
with MCP integration.  

## Content Management System

This example creates an MCP server for managing content with CRUD operations,  
versioning, and search capabilities.  

```python
#!/usr/bin/env python3
import asyncio
import json
import time
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent


@dataclass
class ContentItem:
    """Represents a content item."""
    id: str
    title: str
    content: str
    content_type: str
    author: str
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    version: int = 1
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    published: bool = False

# Content storage
content_items: Dict[str, ContentItem] = {}
content_versions: Dict[str, List[ContentItem]] = {}

# Sample content
content_items["1"] = ContentItem(
    id="1",
    title="Getting Started with Python",
    content="Python is a versatile programming language...",
    content_type="article",
    author="admin",
    tags=["python", "programming", "tutorial"],
    published=True
)

content_items["2"] = ContentItem(
    id="2", 
    title="Advanced Python Concepts",
    content="This article covers advanced Python features...",
    content_type="article",
    author="admin",
    tags=["python", "advanced"],
    published=False
)

def search_content(query: str, filters: Dict[str, Any] = None) -> List[ContentItem]:
    """Search content items."""
    results = []
    filters = filters or {}
    
    for item in content_items.values():
        # Text search
        if query:
            search_text = f"{item.title} {item.content} {' '.join(item.tags)}".lower()
            if query.lower() not in search_text:
                continue
        
        # Filter by content type
        if filters.get("content_type") and item.content_type != filters["content_type"]:
            continue
            
        # Filter by author
        if filters.get("author") and item.author != filters["author"]:
            continue
            
        # Filter by published status
        if "published" in filters and item.published != filters["published"]:
            continue
            
        # Filter by tags
        if filters.get("tags"):
            required_tags = filters["tags"]
            if not all(tag in item.tags for tag in required_tags):
                continue
        
        results.append(item)
    
    # Sort by relevance (most recent first)
    return sorted(results, key=lambda x: x.updated_at, reverse=True)

app = Server("content-management-server")

@app.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List content resources."""
    resources = [
        Resource(
            uri="content://all",
            name="All Content",
            description="List of all content items",
            mimeType="application/json"
        ),
        Resource(
            uri="content://published",
            name="Published Content",
            description="Published content items only",
            mimeType="application/json"
        ),
        Resource(
            uri="content://stats",
            name="Content Statistics",
            description="Content management statistics",
            mimeType="application/json"
        )
    ]
    
    # Add individual content items as resources
    for item in content_items.values():
        resources.append(Resource(
            uri=f"content://item/{item.id}",
            name=item.title,
            description=f"Content item: {item.title} by {item.author}",
            mimeType="text/plain" if item.content_type == "text" else "text/html"
        ))
    
    return resources

@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read content resources."""
    if uri == "content://all":
        items_data = []
        for item in content_items.values():
            items_data.append({
                "id": item.id,
                "title": item.title,
                "content_type": item.content_type,
                "author": item.author,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
                "version": item.version,
                "tags": item.tags,
                "published": item.published,
                "content_preview": item.content[:100] + "..." if len(item.content) > 100 else item.content
            })
        return json.dumps(items_data, indent=2)
    
    elif uri == "content://published":
        published_items = [item for item in content_items.values() if item.published]
        items_data = []
        for item in published_items:
            items_data.append({
                "id": item.id,
                "title": item.title,
                "content": item.content,
                "author": item.author,
                "tags": item.tags,
                "created_at": item.created_at
            })
        return json.dumps(items_data, indent=2)
    
    elif uri == "content://stats":
        total_items = len(content_items)
        published_items = len([item for item in content_items.values() if item.published])
        content_types = {}
        authors = {}
        all_tags = []
        
        for item in content_items.values():
            # Count content types
            content_types[item.content_type] = content_types.get(item.content_type, 0) + 1
            
            # Count authors
            authors[item.author] = authors.get(item.author, 0) + 1
            
            # Collect tags
            all_tags.extend(item.tags)
        
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        stats = {
            "total_items": total_items,
            "published_items": published_items,
            "draft_items": total_items - published_items,
            "content_types": content_types,
            "authors": authors,
            "popular_tags": sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        }
        
        return json.dumps(stats, indent=2)
    
    elif uri.startswith("content://item/"):
        item_id = uri.replace("content://item/", "")
        
        if item_id not in content_items:
            raise ValueError(f"Content item not found: {item_id}")
        
        item = content_items[item_id]
        return item.content
    
    else:
        raise ValueError(f"Unknown resource: {uri}")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Return content management tools."""
    return [
        Tool(
            name="create_content",
            description="Create a new content item",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Content title"},
                    "content": {"type": "string", "description": "Content body"},
                    "content_type": {
                        "type": "string",
                        "enum": ["article", "page", "post", "tutorial"],
                        "default": "article",
                        "description": "Type of content"
                    },
                    "author": {"type": "string", "description": "Content author"},
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Content tags"
                    },
                    "published": {"type": "boolean", "default": False}
                },
                "required": ["title", "content", "author"]
            }
        ),
        Tool(
            name="update_content",
            description="Update an existing content item",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Content ID"},
                    "title": {"type": "string", "description": "Updated title"},
                    "content": {"type": "string", "description": "Updated content"},
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Updated tags"
                    },
                    "published": {"type": "boolean", "description": "Published status"}
                },
                "required": ["id"]
            }
        ),
        Tool(
            name="delete_content",
            description="Delete a content item",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Content ID to delete"}
                },
                "required": ["id"]
            }
        ),
        Tool(
            name="search_content",
            description="Search content items",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "content_type": {"type": "string", "description": "Filter by content type"},
                    "author": {"type": "string", "description": "Filter by author"},
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by tags"
                    },
                    "published": {"type": "boolean", "description": "Filter by published status"}
                }
            }
        ),
        Tool(
            name="get_content_history",
            description="Get version history of a content item",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Content ID"}
                },
                "required": ["id"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute content management tools."""
    
    if name == "create_content":
        title = arguments["title"]
        content = arguments["content"]
        content_type = arguments.get("content_type", "article")
        author = arguments["author"]
        tags = arguments.get("tags", [])
        published = arguments.get("published", False)
        
        # Generate ID
        item_id = str(len(content_items) + 1)
        
        # Create content item
        item = ContentItem(
            id=item_id,
            title=title,
            content=content,
            content_type=content_type,
            author=author,
            tags=tags,
            published=published
        )
        
        content_items[item_id] = item
        
        # Initialize version history
        content_versions[item_id] = [item]
        
        result = {
            "id": item_id,
            "title": title,
            "content_type": content_type,
            "author": author,
            "created_at": item.created_at,
            "published": published,
            "message": "Content created successfully"
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "update_content":
        item_id = arguments["id"]
        
        if item_id not in content_items:
            return [TextContent(
                type="text",
                text=f"Content item not found: {item_id}"
            )]
        
        item = content_items[item_id]
        
        # Save current version to history
        if item_id not in content_versions:
            content_versions[item_id] = []
        
        # Create a copy for version history
        import copy
        old_version = copy.deepcopy(item)
        content_versions[item_id].append(old_version)
        
        # Update item
        if "title" in arguments:
            item.title = arguments["title"]
        if "content" in arguments:
            item.content = arguments["content"]
        if "tags" in arguments:
            item.tags = arguments["tags"]
        if "published" in arguments:
            item.published = arguments["published"]
        
        item.updated_at = time.time()
        item.version += 1
        
        result = {
            "id": item_id,
            "version": item.version,
            "updated_at": item.updated_at,
            "message": "Content updated successfully"
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "delete_content":
        item_id = arguments["id"]
        
        if item_id not in content_items:
            return [TextContent(
                type="text",
                text=f"Content item not found: {item_id}"
            )]
        
        # Remove item and its versions
        del content_items[item_id]
        if item_id in content_versions:
            del content_versions[item_id]
        
        return [TextContent(
            type="text",
            text=f"Content item {item_id} deleted successfully"
        )]
    
    elif name == "search_content":
        query = arguments.get("query", "")
        filters = {
            k: v for k, v in arguments.items() 
            if k != "query" and v is not None
        }
        
        results = search_content(query, filters)
        
        search_results = []
        for item in results:
            search_results.append({
                "id": item.id,
                "title": item.title,
                "content_type": item.content_type,
                "author": item.author,
                "tags": item.tags,
                "published": item.published,
                "created_at": item.created_at,
                "snippet": item.content[:150] + "..." if len(item.content) > 150 else item.content
            })
        
        result = {
            "query": query,
            "filters": filters,
            "total_results": len(search_results),
            "results": search_results
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "get_content_history":
        item_id = arguments["id"]
        
        if item_id not in content_items:
            return [TextContent(
                type="text",
                text=f"Content item not found: {item_id}"
            )]
        
        if item_id not in content_versions:
            return [TextContent(
                type="text",
                text="No version history available"
            )]
        
        history = []
        for version in content_versions[item_id]:
            history.append({
                "version": version.version,
                "title": version.title,
                "updated_at": version.updated_at,
                "author": version.author,
                "content_length": len(version.content)
            })
        
        # Add current version
        current = content_items[item_id]
        history.append({
            "version": current.version,
            "title": current.title,
            "updated_at": current.updated_at,
            "author": current.author,
            "content_length": len(current.content),
            "current": True
        })
        
        result = {
            "item_id": item_id,
            "total_versions": len(history),
            "versions": sorted(history, key=lambda x: x["version"], reverse=True)
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the content management MCP server."""
    options = InitializationOptions(
        server_name="content-management-server",
        server_version="1.0.0",
        capabilities={
            "resources": {},
            "tools": {}
        }
    )
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, options)

if __name__ == "__main__":
    asyncio.run(main())
```

This content management server demonstrates CRUD operations, search  
functionality, and version control for content items. It provides  
a foundation for building content management systems with MCP integration.  

## Testing and Validation Server

This example creates an MCP server for testing and validating other MCP  
implementations, providing comprehensive testing tools and utilities.  

```python
#!/usr/bin/env python3
import asyncio
import json
import time
import subprocess
from typing import Dict, List, Any, Optional
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent


# Test results storage
test_results: Dict[str, Any] = {}
test_suites: Dict[str, List[Dict[str, Any]]] = {}

# Sample test suite
test_suites["basic_mcp"] = [
    {
        "name": "Server Initialization",
        "description": "Test if MCP server initializes correctly",
        "test_type": "initialization",
        "expected_capabilities": ["resources", "tools"]
    },
    {
        "name": "List Resources",
        "description": "Test if server can list resources",
        "test_type": "list_resources",
        "expected_min_count": 0
    },
    {
        "name": "List Tools", 
        "description": "Test if server can list tools",
        "test_type": "list_tools",
        "expected_min_count": 0
    },
    {
        "name": "Resource Access",
        "description": "Test if resources can be accessed",
        "test_type": "read_resource",
        "resource_uri": "test://example"
    }
]

def validate_json_schema(data: Any, schema: Dict[str, Any]) -> List[str]:
    """Simple JSON schema validation."""
    errors = []
    
    if schema.get("type") == "object":
        if not isinstance(data, dict):
            errors.append("Expected object type")
            return errors
            
        # Check required fields
        for field in schema.get("required", []):
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Check properties
        for field, field_schema in schema.get("properties", {}).items():
            if field in data:
                field_errors = validate_json_schema(data[field], field_schema)
                errors.extend([f"{field}: {err}" for err in field_errors])
    
    elif schema.get("type") == "array":
        if not isinstance(data, list):
            errors.append("Expected array type")
        else:
            items_schema = schema.get("items", {})
            for i, item in enumerate(data):
                item_errors = validate_json_schema(item, items_schema)
                errors.extend([f"[{i}]: {err}" for err in item_errors])
    
    elif schema.get("type") == "string":
        if not isinstance(data, str):
            errors.append("Expected string type")
    
    elif schema.get("type") == "number":
        if not isinstance(data, (int, float)):
            errors.append("Expected number type")
    
    elif schema.get("type") == "boolean":
        if not isinstance(data, bool):
            errors.append("Expected boolean type")
    
    return errors

app = Server("testing-validation-server")

@app.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List testing and validation resources."""
    return [
        Resource(
            uri="tests://suites",
            name="Test Suites",
            description="Available test suites",
            mimeType="application/json"
        ),
        Resource(
            uri="tests://results",
            name="Test Results",
            description="Recent test execution results",
            mimeType="application/json"
        ),
        Resource(
            uri="validation://schemas",
            name="Validation Schemas",
            description="JSON schemas for MCP validation",
            mimeType="application/json"
        ),
        Resource(
            uri="docs://mcp-spec",
            name="MCP Specification",
            description="MCP protocol specification reference",
            mimeType="text/markdown"
        )
    ]

@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read testing and validation resources."""
    if uri == "tests://suites":
        return json.dumps(test_suites, indent=2)
    
    elif uri == "tests://results":
        return json.dumps(test_results, indent=2)
    
    elif uri == "validation://schemas":
        mcp_schemas = {
            "initialization_request": {
                "type": "object",
                "properties": {
                    "method": {"type": "string", "enum": ["initialize"]},
                    "params": {
                        "type": "object",
                        "properties": {
                            "protocolVersion": {"type": "string"},
                            "capabilities": {"type": "object"},
                            "clientInfo": {"type": "object"}
                        },
                        "required": ["protocolVersion", "capabilities", "clientInfo"]
                    }
                },
                "required": ["method", "params"]
            },
            "resource": {
                "type": "object",
                "properties": {
                    "uri": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "mimeType": {"type": "string"}
                },
                "required": ["uri", "name"]
            },
            "tool": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "inputSchema": {"type": "object"}
                },
                "required": ["name", "description"]
            }
        }
        return json.dumps(mcp_schemas, indent=2)
    
    elif uri == "docs://mcp-spec":
        mcp_spec = """# MCP Protocol Specification Reference

## Core Concepts

- **Server**: Exposes resources, tools, and prompts
- **Client**: Connects to servers to access capabilities  
- **Transport**: Communication layer (stdio, WebSocket, SSE)
- **Resources**: Data sources and content
- **Tools**: Functions that can be executed
- **Prompts**: Template fragments for AI interactions

## Message Types

### Initialization
- `initialize`: Initialize connection
- `initialized`: Confirm initialization

### Resources  
- `resources/list`: List available resources
- `resources/read`: Read resource content

### Tools
- `tools/list`: List available tools  
- `tools/call`: Execute a tool

### Prompts
- `prompts/list`: List available prompts
- `prompts/get`: Get prompt with arguments

## Error Handling

All errors should include:
- Error code
- Error message
- Optional error data
"""
        return mcp_spec
    
    else:
        raise ValueError(f"Unknown resource: {uri}")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Return testing and validation tools."""
    return [
        Tool(
            name="run_test_suite",
            description="Execute a test suite against an MCP server",
            inputSchema={
                "type": "object",
                "properties": {
                    "suite_name": {
                        "type": "string",
                        "enum": list(test_suites.keys()),
                        "description": "Test suite to execute"
                    },
                    "server_command": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Command to start MCP server"
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 30,
                        "description": "Test timeout in seconds"
                    }
                },
                "required": ["suite_name", "server_command"]
            }
        ),
        Tool(
            name="validate_mcp_response",
            description="Validate an MCP response against schema",
            inputSchema={
                "type": "object",
                "properties": {
                    "response": {"description": "MCP response to validate"},
                    "message_type": {
                        "type": "string",
                        "enum": ["initialization", "list_resources", "list_tools", "call_tool"],
                        "description": "Type of MCP message"
                    }
                },
                "required": ["response", "message_type"]
            }
        ),
        Tool(
            name="benchmark_server",
            description="Benchmark MCP server performance",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_command": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Command to start MCP server"
                    },
                    "operations": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Operations to benchmark"
                    },
                    "iterations": {
                        "type": "integer",
                        "default": 100,
                        "description": "Number of iterations per operation"
                    }
                },
                "required": ["server_command"]
            }
        ),
        Tool(
            name="create_test_case",
            description="Create a new test case",
            inputSchema={
                "type": "object",
                "properties": {
                    "suite_name": {"type": "string", "description": "Test suite name"},
                    "test_name": {"type": "string", "description": "Test case name"},
                    "test_type": {"type": "string", "description": "Type of test"},
                    "description": {"type": "string", "description": "Test description"},
                    "parameters": {"type": "object", "description": "Test parameters"}
                },
                "required": ["suite_name", "test_name", "test_type", "description"]
            }
        ),
        Tool(
            name="generate_test_report",
            description="Generate comprehensive test report",
            inputSchema={
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "enum": ["json", "html", "markdown"],
                        "default": "json",
                        "description": "Report format"
                    }
                }
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute testing and validation tools."""
    
    if name == "run_test_suite":
        suite_name = arguments["suite_name"]
        server_command = arguments["server_command"]
        timeout = arguments.get("timeout", 30)
        
        if suite_name not in test_suites:
            return [TextContent(
                type="text",
                text=f"Test suite '{suite_name}' not found"
            )]
        
        test_suite = test_suites[suite_name]
        results = {
            "suite_name": suite_name,
            "server_command": server_command,
            "started_at": time.time(),
            "tests": []
        }
        
        # Mock test execution (in real implementation, would start server and run tests)
        for test_case in test_suite:
            test_result = {
                "name": test_case["name"],
                "description": test_case["description"],
                "test_type": test_case["test_type"],
                "status": "passed",  # Mock result
                "duration": 0.1,
                "message": "Test executed successfully"
            }
            
            # Add some mock failures for demonstration
            if "Resource Access" in test_case["name"]:
                test_result["status"] = "failed"
                test_result["message"] = "Resource not found: test://example"
            
            results["tests"].append(test_result)
        
        results["completed_at"] = time.time()
        results["duration"] = results["completed_at"] - results["started_at"]
        results["total_tests"] = len(results["tests"])
        results["passed"] = len([t for t in results["tests"] if t["status"] == "passed"])
        results["failed"] = len([t for t in results["tests"] if t["status"] == "failed"])
        
        # Store results
        test_results[f"{suite_name}_{int(time.time())}"] = results
        
        return [TextContent(
            type="text",
            text=json.dumps(results, indent=2)
        )]
    
    elif name == "validate_mcp_response":
        response = arguments["response"]
        message_type = arguments["message_type"]
        
        # Get appropriate schema
        if message_type == "list_resources":
            schema = {
                "type": "object",
                "properties": {
                    "resources": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "uri": {"type": "string"},
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "mimeType": {"type": "string"}
                            },
                            "required": ["uri", "name"]
                        }
                    }
                },
                "required": ["resources"]
            }
        else:
            schema = {"type": "object"}  # Generic schema
        
        # Validate response
        errors = validate_json_schema(response, schema)
        
        validation_result = {
            "message_type": message_type,
            "valid": len(errors) == 0,
            "errors": errors,
            "validated_at": time.time()
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(validation_result, indent=2)
        )]
    
    elif name == "benchmark_server":
        server_command = arguments["server_command"]
        operations = arguments.get("operations", ["list_resources", "list_tools"])
        iterations = arguments.get("iterations", 100)
        
        # Mock benchmark results
        benchmark_results = {
            "server_command": server_command,
            "iterations": iterations,
            "started_at": time.time(),
            "operations": {}
        }
        
        for operation in operations:
            # Simulate benchmarking
            await asyncio.sleep(0.1)  # Mock delay
            
            benchmark_results["operations"][operation] = {
                "total_time": 5.0,  # Mock: 5 seconds total
                "avg_time": 0.05,   # Mock: 50ms average
                "min_time": 0.01,   # Mock: 10ms minimum
                "max_time": 0.1,    # Mock: 100ms maximum
                "requests_per_second": 20,  # Mock: 20 req/s
                "success_rate": 0.98  # Mock: 98% success
            }
        
        benchmark_results["completed_at"] = time.time()
        benchmark_results["total_duration"] = benchmark_results["completed_at"] - benchmark_results["started_at"]
        
        return [TextContent(
            type="text",
            text=json.dumps(benchmark_results, indent=2)
        )]
    
    elif name == "create_test_case":
        suite_name = arguments["suite_name"]
        test_name = arguments["test_name"]
        test_type = arguments["test_type"]
        description = arguments["description"]
        parameters = arguments.get("parameters", {})
        
        if suite_name not in test_suites:
            test_suites[suite_name] = []
        
        test_case = {
            "name": test_name,
            "description": description,
            "test_type": test_type,
            **parameters
        }
        
        test_suites[suite_name].append(test_case)
        
        result = {
            "message": f"Test case '{test_name}' added to suite '{suite_name}'",
            "suite_name": suite_name,
            "test_case": test_case
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "generate_test_report":
        format_type = arguments.get("format", "json")
        
        if format_type == "json":
            report = {
                "generated_at": time.time(),
                "test_suites": len(test_suites),
                "total_test_cases": sum(len(suite) for suite in test_suites.values()),
                "test_results": len(test_results),
                "suites": test_suites,
                "results": test_results
            }
            return [TextContent(
                type="text",
                text=json.dumps(report, indent=2)
            )]
        
        elif format_type == "markdown":
            report = f"""# MCP Test Report

Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- Test Suites: {len(test_suites)}
- Total Test Cases: {sum(len(suite) for suite in test_suites.values())}
- Test Executions: {len(test_results)}

## Test Suites

"""
            for suite_name, tests in test_suites.items():
                report += f"### {suite_name}\n\n"
                for test in tests:
                    report += f"- **{test['name']}**: {test['description']}\n"
                report += "\n"
            
            return [TextContent(type="text", text=report)]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unsupported format: {format_type}"
            )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the testing and validation MCP server."""
    options = InitializationOptions(
        server_name="testing-validation-server",
        server_version="1.0.0",
        capabilities={
            "resources": {},
            "tools": {}
        }
    )
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, options)

if __name__ == "__main__":
    asyncio.run(main())
```

This testing and validation server provides comprehensive tools for testing  
MCP implementations, validating protocol compliance, benchmarking  
performance, and generating detailed test reports.  

## Simple Client Connection

This example demonstrates the most basic MCP client implementation for  
connecting to and interacting with MCP servers.  

```python
#!/usr/bin/env python3
import asyncio
import json
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client


async def simple_mcp_client():
    """Simple MCP client example."""
    
    # Connect to an MCP server
    server_command = ["python", "basic_server.py"]
    
    async with stdio_client(server_command) as (read_stream, write_stream):
        # Create client session
        session = ClientSession(read_stream, write_stream)
        
        # Initialize the session
        await session.initialize()
        print("✅ Connected to MCP server")
        
        # List available resources
        resources_result = await session.list_resources()
        print(f"\n📚 Found {len(resources_result.resources)} resources:")
        for resource in resources_result.resources:
            print(f"  - {resource.name}: {resource.uri}")
        
        # List available tools
        tools_result = await session.list_tools()  
        print(f"\n🔧 Found {len(tools_result.tools)} tools:")
        for tool in tools_result.tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # Read a resource if available
        if resources_result.resources:
            first_resource = resources_result.resources[0]
            print(f"\n📖 Reading resource: {first_resource.uri}")
            
            content = await session.read_resource(first_resource.uri)
            for item in content.contents:
                if hasattr(item, 'text'):
                    print(f"Content: {item.text}")
        
        # Call a tool if available
        if tools_result.tools:
            first_tool = tools_result.tools[0]
            print(f"\n🛠️ Calling tool: {first_tool.name}")
            
            # Example tool call (adjust based on actual tool schema)
            try:
                result = await session.call_tool(first_tool.name, {"test": "value"})
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(f"Result: {content.text}")
            except Exception as e:
                print(f"Tool call failed: {e}")
        
        print("\n👋 Disconnecting...")

if __name__ == "__main__":
    asyncio.run(simple_mcp_client())
```

This simple client demonstrates the basic MCP interaction pattern:  
connection establishment, capability discovery, resource access, and  
tool execution. It provides a foundation for building more complex  
MCP client applications.  

## Advanced Client with Error Handling

This example shows a more robust MCP client with comprehensive error  
handling, retry logic, and connection management.  

```python
#!/usr/bin/env python3
import asyncio
import json
import logging
from typing import Optional, List, Dict, Any
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPClientManager:
    """Advanced MCP client with error handling and retry logic."""
    
    def __init__(self, server_command: List[str], max_retries: int = 3):
        self.server_command = server_command
        self.max_retries = max_retries
        self.session: Optional[ClientSession] = None
        self.stdio_client = None
    
    async def connect(self) -> bool:
        """Connect to MCP server with retry logic."""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Connection attempt {attempt + 1}/{self.max_retries}")
                
                self.stdio_client = stdio_client(self.server_command)
                read_stream, write_stream = await self.stdio_client.__aenter__()
                
                self.session = ClientSession(read_stream, write_stream)
                await self.session.initialize()
                
                logger.info("✅ Successfully connected to MCP server")
                return True
                
            except Exception as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                
                if self.stdio_client:
                    try:
                        await self.stdio_client.__aexit__(None, None, None)
                    except:
                        pass
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error("All connection attempts failed")
                    return False
        
        return False
    
    async def disconnect(self):
        """Safely disconnect from MCP server."""
        if self.session:
            try:
                await self.session.close()
            except Exception as e:
                logger.error(f"Error closing session: {e}")
        
        if self.stdio_client:
            try:
                await self.stdio_client.__aexit__(None, None, None)
            except Exception as e:
                logger.error(f"Error closing stdio client: {e}")
        
        logger.info("👋 Disconnected from MCP server")
    
    async def list_resources(self) -> Optional[List[Dict[str, Any]]]:
        """List available resources with error handling."""
        if not self.session:
            logger.error("Not connected to server")
            return None
        
        try:
            result = await self.session.list_resources()
            resources = []
            
            for resource in result.resources:
                resources.append({
                    "uri": resource.uri,
                    "name": resource.name,
                    "description": resource.description,
                    "mimeType": resource.mimeType
                })
            
            logger.info(f"📚 Listed {len(resources)} resources")
            return resources
            
        except Exception as e:
            logger.error(f"Error listing resources: {e}")
            return None
    
    async def read_resource(self, uri: str) -> Optional[str]:
        """Read resource content with error handling."""
        if not self.session:
            logger.error("Not connected to server")
            return None
        
        try:
            result = await self.session.read_resource(uri)
            
            content = ""
            for item in result.contents:
                if hasattr(item, 'text'):
                    content += item.text
                else:
                    content += f"[Binary content: {len(item.blob)} bytes]"
            
            logger.info(f"📖 Read resource: {uri}")
            return content
            
        except Exception as e:
            logger.error(f"Error reading resource {uri}: {e}")
            return None
    
    async def list_tools(self) -> Optional[List[Dict[str, Any]]]:
        """List available tools with error handling."""
        if not self.session:
            logger.error("Not connected to server")
            return None
        
        try:
            result = await self.session.list_tools()
            tools = []
            
            for tool in result.tools:
                tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": getattr(tool, 'inputSchema', {})
                })
            
            logger.info(f"🔧 Listed {len(tools)} tools")
            return tools
            
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return None
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Optional[str]:
        """Call tool with error handling."""
        if not self.session:
            logger.error("Not connected to server")
            return None
        
        try:
            result = await self.session.call_tool(name, arguments)
            
            response = ""
            for content in result.content:
                if hasattr(content, 'text'):
                    response += content.text
                else:
                    response += f"[Binary result: {len(content.blob)} bytes]"
            
            logger.info(f"🛠️ Called tool: {name}")
            return response
            
        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            return None
    
    async def health_check(self) -> bool:
        """Check if connection is healthy."""
        try:
            # Try a simple operation
            await self.list_resources()
            return True
        except:
            return False

async def demo_advanced_client():
    """Demonstrate advanced MCP client usage."""
    client = MCPClientManager(["python", "basic_server.py"])
    
    try:
        # Connect with retry logic
        if not await client.connect():
            logger.error("Failed to connect to server")
            return
        
        # Discover capabilities
        resources = await client.list_resources()
        tools = await client.list_tools()
        
        # Interactive mode
        print("\n🤖 Interactive MCP Client")
        print("Commands: resources, tools, read <uri>, call <tool> <args>, health, quit")
        
        while True:
            try:
                command = input("\n> ").strip().split()
                if not command:
                    continue
                
                if command[0] == "quit":
                    break
                
                elif command[0] == "resources":
                    resources = await client.list_resources()
                    if resources:
                        print(json.dumps(resources, indent=2))
                
                elif command[0] == "tools":
                    tools = await client.list_tools()
                    if tools:
                        print(json.dumps(tools, indent=2))
                
                elif command[0] == "read" and len(command) > 1:
                    content = await client.read_resource(command[1])
                    if content:
                        print(content)
                
                elif command[0] == "call" and len(command) > 2:
                    tool_name = command[1]
                    try:
                        args = json.loads(" ".join(command[2:]))
                        result = await client.call_tool(tool_name, args)
                        if result:
                            print(result)
                    except json.JSONDecodeError:
                        print("❌ Invalid JSON arguments")
                
                elif command[0] == "health":
                    healthy = await client.health_check()
                    print(f"Connection healthy: {healthy}")
                
                else:
                    print("❌ Unknown command")
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Command error: {e}")
    
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(demo_advanced_client())
```

This advanced client demonstrates production-ready patterns including  
connection retry logic, comprehensive error handling, health checking,  
and interactive operation modes for robust MCP client applications.  

## Streaming Data Server

This example shows how to create an MCP server that handles streaming  
data with real-time updates and subscription management.  

```python
#!/usr/bin/env python3
import asyncio
import json
import time
import random
from typing import Dict, Set, AsyncGenerator
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent


# Streaming data storage
active_streams: Dict[str, bool] = {}
stream_subscribers: Dict[str, Set[str]] = {}
stream_data: Dict[str, list] = {}

async def generate_sensor_data() -> AsyncGenerator[Dict[str, float], None]:
    """Generate continuous sensor data."""
    while True:
        data = {
            "timestamp": time.time(),
            "temperature": round(random.uniform(20, 30), 2),
            "humidity": round(random.uniform(40, 80), 2),
            "pressure": round(random.uniform(1010, 1025), 2)
        }
        yield data
        await asyncio.sleep(1)  # 1 second intervals

async def generate_stock_prices() -> AsyncGenerator[Dict[str, Any], None]:
    """Generate streaming stock price data."""
    stocks = ["AAPL", "GOOGL", "MSFT", "TSLA"]
    base_prices = {"AAPL": 180, "GOOGL": 120, "MSFT": 300, "TSLA": 250}
    
    while True:
        for stock in stocks:
            change = random.uniform(-2, 2)
            base_prices[stock] = max(1, base_prices[stock] + change)
            
            data = {
                "timestamp": time.time(),
                "symbol": stock,
                "price": round(base_prices[stock], 2),
                "change": round(change, 2)
            }
            yield data
        
        await asyncio.sleep(0.5)  # 500ms intervals

async def stream_manager(stream_name: str, generator_func):
    """Manage a data stream."""
    if stream_name not in stream_data:
        stream_data[stream_name] = []
    
    active_streams[stream_name] = True
    
    async for data in generator_func():
        if not active_streams.get(stream_name, False):
            break
        
        # Store data point
        stream_data[stream_name].append(data)
        
        # Keep only last 1000 points
        if len(stream_data[stream_name]) > 1000:
            stream_data[stream_name] = stream_data[stream_name][-1000:]
        
        # In a real implementation, this would notify subscribers
        print(f"📊 {stream_name}: {data}")
        
    active_streams[stream_name] = False

app = Server("streaming-data-server")

@app.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List streaming data resources."""
    resources = [
        Resource(
            uri="stream://sensors/current",
            name="Current Sensor Data",
            description="Latest sensor readings",
            mimeType="application/json"
        ),
        Resource(
            uri="stream://stocks/current",
            name="Current Stock Prices",
            description="Latest stock price data",
            mimeType="application/json"
        ),
        Resource(
            uri="stream://sensors/history",
            name="Sensor History",
            description="Historical sensor data",
            mimeType="application/json"
        ),
        Resource(
            uri="stream://stocks/history",
            name="Stock Price History",
            description="Historical stock price data",
            mimeType="application/json"
        )
    ]
    
    return resources

@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read streaming data resources."""
    if uri == "stream://sensors/current":
        if "sensors" in stream_data and stream_data["sensors"]:
            return json.dumps(stream_data["sensors"][-1], indent=2)
        else:
            return json.dumps({"message": "No sensor data available"}, indent=2)
    
    elif uri == "stream://stocks/current":
        if "stocks" in stream_data and stream_data["stocks"]:
            # Get latest price for each stock
            latest_prices = {}
            for data_point in reversed(stream_data["stocks"]):
                symbol = data_point["symbol"]
                if symbol not in latest_prices:
                    latest_prices[symbol] = data_point
            
            return json.dumps(latest_prices, indent=2)
        else:
            return json.dumps({"message": "No stock data available"}, indent=2)
    
    elif uri == "stream://sensors/history":
        if "sensors" in stream_data:
            # Return last 50 readings
            recent_data = stream_data["sensors"][-50:]
            return json.dumps(recent_data, indent=2)
        else:
            return json.dumps([], indent=2)
    
    elif uri == "stream://stocks/history":
        if "stocks" in stream_data:
            # Return last 100 readings
            recent_data = stream_data["stocks"][-100:]
            return json.dumps(recent_data, indent=2)
        else:
            return json.dumps([], indent=2)
    
    else:
        raise ValueError(f"Unknown resource: {uri}")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Return streaming data tools."""
    return [
        Tool(
            name="start_stream",
            description="Start a data stream",
            inputSchema={
                "type": "object",
                "properties": {
                    "stream_name": {
                        "type": "string",
                        "enum": ["sensors", "stocks"],
                        "description": "Stream to start"
                    }
                },
                "required": ["stream_name"]
            }
        ),
        Tool(
            name="stop_stream",
            description="Stop a data stream",
            inputSchema={
                "type": "object",
                "properties": {
                    "stream_name": {
                        "type": "string",
                        "enum": ["sensors", "stocks"],
                        "description": "Stream to stop"
                    }
                },
                "required": ["stream_name"]
            }
        ),
        Tool(
            name="get_stream_status",
            description="Get status of all streams",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="query_stream_data",
            description="Query stream data with filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "stream_name": {"type": "string", "description": "Stream name"},
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 1000,
                        "default": 100,
                        "description": "Maximum number of records"
                    },
                    "start_time": {"type": "number", "description": "Start timestamp"},
                    "end_time": {"type": "number", "description": "End timestamp"}
                },
                "required": ["stream_name"]
            }
        ),
        Tool(
            name="calculate_stream_stats",
            description="Calculate statistics for stream data",
            inputSchema={
                "type": "object",
                "properties": {
                    "stream_name": {"type": "string", "description": "Stream name"},
                    "metric": {"type": "string", "description": "Metric to analyze"}
                },
                "required": ["stream_name", "metric"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute streaming data tools."""
    
    if name == "start_stream":
        stream_name = arguments["stream_name"]
        
        if active_streams.get(stream_name, False):
            return [TextContent(
                type="text",
                text=f"Stream '{stream_name}' is already running"
            )]
        
        # Start the appropriate stream
        if stream_name == "sensors":
            asyncio.create_task(stream_manager("sensors", generate_sensor_data))
        elif stream_name == "stocks":
            asyncio.create_task(stream_manager("stocks", generate_stock_prices))
        
        return [TextContent(
            type="text",
            text=f"✅ Started stream: {stream_name}"
        )]
    
    elif name == "stop_stream":
        stream_name = arguments["stream_name"]
        
        if not active_streams.get(stream_name, False):
            return [TextContent(
                type="text",
                text=f"Stream '{stream_name}' is not running"
            )]
        
        active_streams[stream_name] = False
        
        return [TextContent(
            type="text",
            text=f"⏹️ Stopped stream: {stream_name}"
        )]
    
    elif name == "get_stream_status":
        status = {
            "streams": {},
            "total_active": 0,
            "data_points": {}
        }
        
        for stream_name in ["sensors", "stocks"]:
            is_active = active_streams.get(stream_name, False)
            status["streams"][stream_name] = {
                "active": is_active,
                "data_points": len(stream_data.get(stream_name, []))
            }
            
            if is_active:
                status["total_active"] += 1
            
            status["data_points"][stream_name] = len(stream_data.get(stream_name, []))
        
        return [TextContent(
            type="text",
            text=json.dumps(status, indent=2)
        )]
    
    elif name == "query_stream_data":
        stream_name = arguments["stream_name"]
        limit = arguments.get("limit", 100)
        start_time = arguments.get("start_time")
        end_time = arguments.get("end_time")
        
        if stream_name not in stream_data:
            return [TextContent(
                type="text",
                text=f"No data available for stream: {stream_name}"
            )]
        
        data = stream_data[stream_name]
        
        # Apply time filters
        if start_time or end_time:
            filtered_data = []
            for point in data:
                timestamp = point.get("timestamp", 0)
                
                if start_time and timestamp < start_time:
                    continue
                if end_time and timestamp > end_time:
                    continue
                
                filtered_data.append(point)
            
            data = filtered_data
        
        # Apply limit
        data = data[-limit:] if limit < len(data) else data
        
        result = {
            "stream_name": stream_name,
            "total_points": len(data),
            "data": data
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "calculate_stream_stats":
        stream_name = arguments["stream_name"]
        metric = arguments["metric"]
        
        if stream_name not in stream_data:
            return [TextContent(
                type="text",
                text=f"No data available for stream: {stream_name}"
            )]
        
        data = stream_data[stream_name]
        
        if not data:
            return [TextContent(
                type="text",
                text="No data points available for statistics"
            )]
        
        # Extract metric values
        values = []
        for point in data:
            if metric in point and isinstance(point[metric], (int, float)):
                values.append(point[metric])
        
        if not values:
            return [TextContent(
                type="text",
                text=f"No numeric data found for metric: {metric}"
            )]
        
        # Calculate statistics
        stats = {
            "stream_name": stream_name,
            "metric": metric,
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1] if values else None
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(stats, indent=2)
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the streaming data MCP server."""
    print("🚀 Starting Streaming Data MCP Server")
    
    options = InitializationOptions(
        server_name="streaming-data-server",
        server_version="1.0.0",
        capabilities={
            "resources": {},
            "tools": {}
        }
    )
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, options)

if __name__ == "__main__":
    asyncio.run(main())
```

This streaming server demonstrates real-time data handling with continuous  
data generation, stream management, historical data storage, and statistical  
analysis capabilities for building live data applications.  

## Plugin Architecture Server

This example demonstrates how to create an MCP server with a plugin  
architecture for extending functionality dynamically.  

```python
#!/usr/bin/env python3
import asyncio
import json
import importlib
import inspect
from typing import Dict, Any, Callable, List
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent


class Plugin:
    """Base class for MCP plugins."""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.version = "1.0.0"
        self.description = "Base plugin"
    
    async def initialize(self):
        """Initialize plugin resources."""
        pass
    
    async def cleanup(self):
        """Clean up plugin resources."""
        pass
    
    def get_resources(self) -> List[Resource]:
        """Return plugin resources."""
        return []
    
    def get_tools(self) -> List[Tool]:
        """Return plugin tools."""
        return []
    
    async def handle_resource(self, uri: str) -> str:
        """Handle resource requests."""
        raise ValueError(f"Unknown resource: {uri}")
    
    async def handle_tool(self, name: str, arguments: dict) -> List[TextContent]:
        """Handle tool calls."""
        raise ValueError(f"Unknown tool: {name}")

class MathPlugin(Plugin):
    """Math operations plugin."""
    
    def __init__(self):
        super().__init__()
        self.description = "Mathematical operations and calculations"
    
    def get_resources(self) -> List[Resource]:
        return [
            Resource(
                uri="math://constants",
                name="Mathematical Constants",
                description="Common mathematical constants",
                mimeType="application/json"
            )
        ]
    
    def get_tools(self) -> List[Tool]:
        return [
            Tool(
                name="calculate",
                description="Perform mathematical calculations",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "Mathematical expression"},
                        "precision": {"type": "integer", "default": 2}
                    },
                    "required": ["expression"]
                }
            ),
            Tool(
                name="factorial",
                description="Calculate factorial of a number",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "number": {"type": "integer", "minimum": 0, "maximum": 20}
                    },
                    "required": ["number"]
                }
            )
        ]
    
    async def handle_resource(self, uri: str) -> str:
        if uri == "math://constants":
            import math
            constants = {
                "pi": math.pi,
                "e": math.e,
                "tau": math.tau,
                "golden_ratio": (1 + math.sqrt(5)) / 2
            }
            return json.dumps(constants, indent=2)
        else:
            return await super().handle_resource(uri)
    
    async def handle_tool(self, name: str, arguments: dict) -> List[TextContent]:
        if name == "calculate":
            expression = arguments["expression"]
            precision = arguments.get("precision", 2)
            
            try:
                # Simple and safe expression evaluation
                import math
                allowed_names = {
                    k: v for k, v in math.__dict__.items() 
                    if not k.startswith("__")
                }
                allowed_names.update({"abs": abs, "round": round})
                
                result = eval(expression, {"__builtins__": {}}, allowed_names)
                
                if isinstance(result, float):
                    result = round(result, precision)
                
                return [TextContent(
                    type="text",
                    text=f"Result: {result}"
                )]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
        
        elif name == "factorial":
            number = arguments["number"]
            
            import math
            result = math.factorial(number)
            
            return [TextContent(
                type="text",
                text=f"Factorial of {number} is {result}"
            )]
        
        else:
            return await super().handle_tool(name, arguments)

class TextPlugin(Plugin):
    """Text processing plugin."""
    
    def __init__(self):
        super().__init__()
        self.description = "Text processing and manipulation operations"
    
    def get_tools(self) -> List[Tool]:
        return [
            Tool(
                name="text_stats",
                description="Get statistics about text",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to analyze"}
                    },
                    "required": ["text"]
                }
            ),
            Tool(
                name="transform_text",
                description="Transform text in various ways",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to transform"},
                        "operation": {
                            "type": "string",
                            "enum": ["uppercase", "lowercase", "title", "reverse"],
                            "description": "Transformation operation"
                        }
                    },
                    "required": ["text", "operation"]
                }
            )
        ]
    
    async def handle_tool(self, name: str, arguments: dict) -> List[TextContent]:
        if name == "text_stats":
            text = arguments["text"]
            
            stats = {
                "character_count": len(text),
                "word_count": len(text.split()),
                "line_count": len(text.splitlines()),
                "paragraph_count": len([p for p in text.split('\n\n') if p.strip()]),
                "uppercase_count": sum(1 for c in text if c.isupper()),
                "lowercase_count": sum(1 for c in text if c.islower()),
                "digit_count": sum(1 for c in text if c.isdigit())
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(stats, indent=2)
            )]
        
        elif name == "transform_text":
            text = arguments["text"]
            operation = arguments["operation"]
            
            if operation == "uppercase":
                result = text.upper()
            elif operation == "lowercase":
                result = text.lower()
            elif operation == "title":
                result = text.title()
            elif operation == "reverse":
                result = text[::-1]
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            return [TextContent(type="text", text=result)]
        
        else:
            return await super().handle_tool(name, arguments)

# Plugin manager
class PluginManager:
    """Manages plugin lifecycle and interactions."""
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
    
    async def load_plugin(self, plugin_class):
        """Load and initialize a plugin."""
        plugin = plugin_class()
        await plugin.initialize()
        self.plugins[plugin.name] = plugin
        return plugin
    
    async def unload_plugin(self, plugin_name: str):
        """Unload and cleanup a plugin."""
        if plugin_name in self.plugins:
            await self.plugins[plugin_name].cleanup()
            del self.plugins[plugin_name]
    
    def get_all_resources(self) -> List[Resource]:
        """Get resources from all plugins."""
        resources = []
        for plugin in self.plugins.values():
            resources.extend(plugin.get_resources())
        return resources
    
    def get_all_tools(self) -> List[Tool]:
        """Get tools from all plugins."""
        tools = []
        for plugin in self.plugins.values():
            tools.extend(plugin.get_tools())
        return tools
    
    async def handle_resource_request(self, uri: str) -> str:
        """Route resource request to appropriate plugin."""
        for plugin in self.plugins.values():
            try:
                return await plugin.handle_resource(uri)
            except ValueError:
                continue
        
        raise ValueError(f"No plugin can handle resource: {uri}")
    
    async def handle_tool_request(self, name: str, arguments: dict) -> List[TextContent]:
        """Route tool request to appropriate plugin."""
        for plugin in self.plugins.values():
            try:
                return await plugin.handle_tool(name, arguments)
            except ValueError:
                continue
        
        raise ValueError(f"No plugin can handle tool: {name}")

# Initialize plugin manager and server
plugin_manager = PluginManager()
app = Server("plugin-architecture-server")

@app.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List all plugin resources plus core resources."""
    resources = plugin_manager.get_all_resources()
    
    # Add core plugin management resources
    resources.extend([
        Resource(
            uri="plugins://list",
            name="Plugin List",
            description="List of loaded plugins",
            mimeType="application/json"
        ),
        Resource(
            uri="plugins://info",
            name="Plugin Information",
            description="Detailed plugin information",
            mimeType="application/json"
        )
    ])
    
    return resources

@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Handle resource requests."""
    if uri == "plugins://list":
        plugin_list = [
            {
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description
            }
            for plugin in plugin_manager.plugins.values()
        ]
        return json.dumps(plugin_list, indent=2)
    
    elif uri == "plugins://info":
        plugin_info = {}
        for name, plugin in plugin_manager.plugins.items():
            plugin_info[name] = {
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description,
                "resources": len(plugin.get_resources()),
                "tools": len(plugin.get_tools())
            }
        return json.dumps(plugin_info, indent=2)
    
    else:
        # Try plugin handlers
        return await plugin_manager.handle_resource_request(uri)

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List all plugin tools plus core tools."""
    tools = plugin_manager.get_all_tools()
    
    # Add core plugin management tools
    tools.extend([
        Tool(
            name="list_plugins",
            description="List loaded plugins",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="plugin_info",
            description="Get information about a specific plugin",
            inputSchema={
                "type": "object",
                "properties": {
                    "plugin_name": {"type": "string", "description": "Plugin name"}
                },
                "required": ["plugin_name"]
            }
        )
    ])
    
    return tools

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "list_plugins":
        plugins = [
            {
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description
            }
            for plugin in plugin_manager.plugins.values()
        ]
        
        return [TextContent(
            type="text",
            text=json.dumps(plugins, indent=2)
        )]
    
    elif name == "plugin_info":
        plugin_name = arguments["plugin_name"]
        
        if plugin_name not in plugin_manager.plugins:
            return [TextContent(
                type="text",
                text=f"Plugin not found: {plugin_name}"
            )]
        
        plugin = plugin_manager.plugins[plugin_name]
        info = {
            "name": plugin.name,
            "version": plugin.version,
            "description": plugin.description,
            "resources": [
                {"uri": r.uri, "name": r.name, "description": r.description}
                for r in plugin.get_resources()
            ],
            "tools": [
                {"name": t.name, "description": t.description}
                for t in plugin.get_tools()
            ]
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(info, indent=2)
        )]
    
    else:
        # Try plugin handlers
        return await plugin_manager.handle_tool_request(name, arguments)

async def main():
    """Run the plugin architecture MCP server."""
    print("🔌 Starting Plugin Architecture MCP Server")
    
    # Load built-in plugins
    await plugin_manager.load_plugin(MathPlugin)
    await plugin_manager.load_plugin(TextPlugin)
    
    print(f"✅ Loaded {len(plugin_manager.plugins)} plugins")
    
    options = InitializationOptions(
        server_name="plugin-architecture-server",
        server_version="1.0.0",
        capabilities={
            "resources": {},
            "tools": {}
        }
    )
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, options)
    finally:
        # Cleanup plugins
        for plugin_name in list(plugin_manager.plugins.keys()):
            await plugin_manager.unload_plugin(plugin_name)
        print("🧹 Cleaned up all plugins")

if __name__ == "__main__":
    asyncio.run(main())
```

This plugin architecture server demonstrates modular MCP design with  
dynamic plugin loading, resource and tool aggregation, and plugin  
lifecycle management for building extensible MCP applications.  

## Best Practices Summary

Based on the examples above, here are key best practices for Python MCP  
development:  

```python
# Essential imports for most MCP servers
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

# Always use proper error handling
async def handle_with_errors():
    try:
        # MCP operations
        pass
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

# Use type hints for better code quality
from typing import Dict, List, Any, Optional

# Structure servers with clear separation
class MyMCPServer:
    def __init__(self):
        self.app = Server("my-server")
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.app.list_resources()
        async def handle_list_resources():
            return self.get_resources()
        
        @self.app.read_resource()  
        async def handle_read_resource(uri: str):
            return await self.read_resource(uri)
    
    async def get_resources(self) -> List[Resource]:
        return []
    
    async def read_resource(self, uri: str) -> str:
        return ""

# Always validate inputs
def validate_tool_arguments(arguments: dict, schema: dict) -> List[str]:
    errors = []
    for field in schema.get("required", []):
        if field not in arguments:
            errors.append(f"Missing required field: {field}")
    return errors

# Use proper logging
import logging
logger = logging.getLogger(__name__)

# Implement graceful shutdown
async def main():
    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, options)
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
```

## Key Design Principles

**Resource Design**: Resources should represent stable, addressable content  
that clients can reliably access. Use clear URI schemes and provide  
comprehensive metadata.  

**Tool Design**: Tools should be focused, well-documented functions with  
clear input schemas and predictable outputs. Handle errors gracefully  
and provide meaningful feedback.  

**Security**: Always validate inputs, implement proper authentication  
and authorization, use rate limiting for production servers, and  
sanitize outputs to prevent injection attacks.  

**Performance**: Use connection pooling for databases, implement caching  
where appropriate, handle concurrent requests properly, and monitor  
resource usage.  

**Testing**: Write comprehensive tests, validate MCP protocol compliance,  
test error conditions, and benchmark performance under load.  

These 30 examples provide a comprehensive foundation for building  
production-ready MCP servers in Python, covering everything from basic  
implementations to advanced patterns and best practices.  
