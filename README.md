# Multi Agent System with Multiple MCP Servers

This project showcases a Multi Agent System which connects to multiple MCP servers and brings the power of multiple MCPs to a single application.

## Features

- **Multiple Local MCP Servers:**  
  - Get financial data using the Yahoo Finance API.
  - Manage the lifecycle of an object in a Kusto database.
- **Configurable MCP Servers:**  
  - Configuration is managed via `mcp-config.json`:
    - **Local MCP servers:**  
      - `review_mcp_server`: Manage review object lifecycle in Kusto DB  
      - `rh_mcp_server`: Manage portfolio of Robinhood stocks
    - **External MCP servers:**  
      - Brave Search MCP: Search the internet  
      - Playwright MCP
- **Client Application:**  
  - Connects to both local and external MCP servers.
- **Team of Autogen AI Agents:**  
  - One agent per MCP server, each with its own tools.
  - One agent to breakdown user query and assign task to appropriate agent
  - one agent to format the response provided to user
  - Agents collaborate as a group.

## How to Run

1. **Install Python dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

2. **Run the Robinhood MCP server:**
    ```sh
    python rh_mcp_server.py
    ```

3. **Run the Reviews MCP server:**
    ```sh
    python reviews_mcp_server.py
    ```

4. **Run the MCP client:**
    ```sh
    python client-main.py
    ```

This will bring up a prompt where you can chat with the AI agents.  
Based on your question, the appropriate agent will be invoked and the requested operation will be performed automatically.
