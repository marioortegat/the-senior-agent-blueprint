# MCP SQLite Server

A Model Context Protocol (MCP) server that enables AI agents to interact with a SQLite database for lead management operations. This project demonstrates how to build custom tools that Large Language Models can use to perform database operations through natural language.

## Overview

This server exposes a set of tools that allow AI agents (via n8n, Claude Desktop, or any MCP-compatible client) to:

- Add new leads to a CRM database
- Search leads by email or name
- List all leads with pipeline statistics
- Update lead status through the sales funnel

## Prerequisites

### Required Software

- **Python 3.10+**: The minimum Python version required for MCP SDK compatibility
- **uv**: A modern, fast Python package manager (recommended for senior developers)
- **FastMCP**: The Pythonic MCP library for building AI tool servers

### Installing uv

uv is a modern replacement for pip and virtualenv. It provides faster dependency resolution and better reproducibility.

**Windows (PowerShell):**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify installation:
```bash
uv --version
```

## Project Structure

```
Chapter_03_MCP/
├── main.py           # MCP server implementation
├── pyproject.toml    # Project dependencies and metadata
├── README.md         # This documentation
└── leads.db          # SQLite database (created on first run)
```

## Installation

1. **Navigate to the project directory:**
   ```bash
   cd 02_Code_Repository/Chapter_03_MCP
   ```

2. **Create virtual environment and install dependencies using uv:**
   ```bash
   uv venv
   uv pip install -e .
   ```

   Or install with pip:
   ```bash
   pip install -r requirements.txt
   ```

## Code Architecture

### Block A: Pydantic Models

Pydantic provides strict type validation at runtime. When the model expects an "email", Pydantic ensures it's a valid string format. This prevents runtime errors and gives the LLM clear schemas to work with.

```python
class Lead(BaseModel):
    name: str = Field(..., description="Full name of the lead")
    email: str = Field(..., description="Email address of the lead")
    value: float = Field(..., description="Monetary value in USD")
```

### Block B: Database Connection

Simple SQLite connection with automatic table creation. The database file is created in the same directory as the script on first run.

```python
def init_database() -> None:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            value REAL NOT NULL DEFAULT 0.0,
            status TEXT NOT NULL DEFAULT 'new'
        )
    """)
```

### Block C: Tool Definitions

The `@mcp.tool()` decorator exposes functions as tools that AI agents can call. The docstring is critical because it's what the LLM reads to understand how to use each tool.

Available tools:
- `get_lead_by_email(email)`: Look up a specific lead by email
- `get_lead_by_name(name)`: Search leads by name (partial match)
- `add_new_lead(name, email, value)`: Create a new lead record
- `list_all_leads()`: Get all leads with summary stats
- `update_lead_status(email, new_status)`: Update lead pipeline status

### Block D: Server Entry Point

The stdio_server uses standard input/output for communication. This is the protocol that MCP clients use to send requests and receive responses.

```python
async with stdio_server() as (read_stream, write_stream):
    await mcp.run(read_stream, write_stream, options)
```

## Running the Server

### Local Testing

Run the server directly:
```bash
uv run main.py
```

Or with standard Python:
```bash
python main.py
```

### Testing with MCP Inspector

Before integrating with Claude Desktop or n8n, validate your server using the MCP Inspector:

1. **Run the Inspector with your server:**
   ```bash
   npx @modelcontextprotocol/inspector .\.venv\Scripts\python.exe main.py
   ```
   
   On macOS/Linux:
   ```bash
   npx @modelcontextprotocol/inspector .venv/bin/python main.py
   ```

2. **Open the Inspector interface:**
   - The browser will open automatically at `http://localhost:6274`
   - Click "Connect" if not already connected

3. **Test your tools:**
   - Navigate to the "Tools" tab in the left panel
   - You should see all 5 tools: `add_new_lead`, `get_lead_by_email`, `get_lead_by_name`, `list_all_leads`, `update_lead_status`
   - Click on any tool to test it with sample parameters

## Integration with Claude Desktop

Claude Desktop natively supports MCP servers, allowing Claude to use your database tools directly in conversation.

### Configuration Steps

1. **Locate the Claude Desktop config file:**
   
   - **Windows**: `C:\Users\YOUR_USERNAME\AppData\Roaming\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Copy the template from this project:**
   
   A template file is provided: `claude_desktop_config.example.json`

3. **Edit the config with your paths:**
   
   ```json
   {
       "mcpServers": {
           "sqlite-leads": {
               "command": "C:/path/to/your/.venv/Scripts/python.exe",
               "args": [
                   "C:/path/to/your/main.py"
               ]
           }
       }
   }
   ```
   
   **Important**: Use forward slashes `/` even on Windows, or escape backslashes as `\\`.

4. **Restart Claude Desktop**
   
   After saving the config, completely close and reopen Claude Desktop.

5. **Verify the connection:**
   
   - Look for the tools icon (hammer) in the chat input area
   - Click it to see the available tools from your MCP server

### Example Conversation with Claude

**You**: "Add a new lead named John Smith with email john@example.com and value $10,000"

**Claude**: *Uses the `add_new_lead` tool*

"I've added John Smith to your leads database. Here are the details:
- Name: John Smith
- Email: john@example.com
- Value: $10,000.00
- Status: new"

**You**: "What is the value of all leads in the database?"

**Claude**: *Uses the `list_all_leads` tool*

"Your current pipeline has 3 leads with a total value of $25,000.00..."

## Integration with n8n

### Configuration Steps

1. **Open n8n and create a new workflow**

2. **Add an AI Agent node:**
   - Use the "AI Agent" node (not the basic Execute Command)
   - Configure it to use your preferred LLM (OpenAI, Anthropic, etc.)

3. **Configure MCP Tool Connection:**
   
   In the AI Agent node settings, add an MCP server tool:
   
   - **Command**: `uv run main.py`
   - **Working Directory**: Full path to `Chapter_03_MCP` folder
   - **Name**: `sqlite-leads-server`

   Alternative using Python directly:
   - **Command**: `python main.py`
   - **Working Directory**: Full path to `Chapter_03_MCP` folder

4. **Set the Agent System Prompt:**
   ```
   You are a helpful CRM assistant with access to a leads database.
   You can add new leads, search for existing leads by name or email,
   list all leads in the pipeline, and update lead statuses.
   Use the available database tools to help the user manage their leads.
   ```

### Example Conversation

**User**: "What is the value of the client Mario?"

**Agent Reasoning**: "I need to search for a lead named Mario using the get_lead_by_name tool."

**Tool Call**: `get_lead_by_name(name="Mario")`

**Response**: "The client Mario Garcia has a value of $5,000.00 and is currently in 'qualified' status."

### Workflow Example

```
[Chat Trigger] → [AI Agent with MCP Tools] → [Respond to User]
```

The AI Agent node handles:
- Receiving user messages
- Determining which tools to call based on the query
- Executing MCP tool calls via stdio
- Formatting responses for the user

## Debugging Common Issues

### Path Not Found

**Problem**: n8n cannot find the Python script or uv command.

**Solution**: 
- Use absolute paths in n8n configuration
- Ensure uv is in your system PATH
- On Windows, you may need to specify `uv.exe` full path

### Permission Errors

**Problem**: Python or the database cannot be accessed.

**Solution**:
- Run n8n with appropriate permissions
- Ensure the `leads.db` file location is writable
- On Linux/macOS, check file permissions with `chmod`

### Server Not Responding

**Problem**: The MCP Inspector or n8n cannot connect to the server.

**Solution**:
- Verify the server starts without errors: `python main.py`
- Check for port conflicts with other processes
- Ensure all dependencies are installed: `uv pip install mcp pydantic`

### Invalid Tool Schema

**Problem**: LLM cannot understand how to use tools.

**Solution**:
- Ensure all tool docstrings are descriptive
- Include parameter descriptions in Field() definitions
- Restart the server after making changes

## Summary

You have created an MCP server that allows AI agents to interact with a SQL database without writing a single SQL query manually in your automation workflow. The agent uses natural language to understand user requests and translates them into appropriate database operations.

Key takeaways:
- Pydantic models ensure type safety for all tool parameters
- Tool docstrings are critical for LLM understanding
- The stdio protocol enables communication with any MCP-compatible client
- n8n's AI Agent node can connect to MCP servers for enhanced capabilities
