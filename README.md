# Multi Agent System with Multiple MCP Servers

This project showcases a Multi Agent System which connects to multiple MCP servers and brings the power of multiple MCPs to a single application.

## Details

1. **Creates multiple MCP Servers locally** which expose tools to perform the following operations:
    - Get financial data using the Yahoo Finance API.
    - Manage the lifecycle of an object in a Kusto database.
2. **Creates a config file (`mcp-config.json`)** which stores configuration for local and external MCP servers.
3. **Creates clients** which connect to local and external MCP servers.
4. **Creates a team of Autogen AI agents:**
    - One agent per MCP server, assigning MCP server tools to that agent.
    - Creates a group of AI agents that collaborate.

## How to Run

1. **Install Python dependencies** using pip:
    ```
    pip install -r requirements.txt
    ```
2. **Run the finance MCP server:**
    ```
    python finance_mcp_server.py
    ```
3. **Run the reviews MCP server:**
    ```
    python reviews_mcp_server.py
    ```
4. **Run the MCP client:**
    ```
    python client_main.py
    ```

This will bring up a prompt where you can chat with the AI agents.

Based on your question, the appropriate agent will be invoked and the requested operation will be performed automatically.
