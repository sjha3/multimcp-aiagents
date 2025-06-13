from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools
import asyncio
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
import os
from dotenv import load_dotenv

# Define server parameters to run the calculator server
server_params = StdioServerParams(
    command="python",              # The executable to run
    args=["main.py"], # The server script (you’ll need to create this)
    env=None                       # Optional: environment variables (None uses defaults)
)

async def main() -> None:
    load_dotenv(override=True)  # Load environment variables from .env file
    print("Azure end point:", os.getenv("azure_endpoint"))
    # Get the fetch tool from mcp-server-fetch.
    fetch_mcp_server = StdioServerParams(command="uvx", args=["mcp-server-fetch"])
    tools = await mcp_server_tools(fetch_mcp_server)
    
    model_client = AzureOpenAIChatCompletionClient(
            azure_endpoint=os.getenv("azure_endpoint"),
            azure_deployment=os.getenv("azure_deployment"),
            api_version=os.getenv("api_version"),
            api_key=os.getenv("api_key"),
            model=os.getenv("azure_model_name"),    
    )
    agent = AssistantAgent(name="fetcher", model_client=model_client, tools=tools, reflect_on_tool_use=True)  # type: ignore
    # Create an agent that can use the fetch tool.
    #model_client = OpenAIChatCompletionClient(model="gpt-4o")
    #agent = AssistantAgent(name="fetcher", model_client=model_client, tools=tools, reflect_on_tool_use=True)  # type: ignore

    # Let the agent fetch the content of a URL and summarize it.
    result = await agent.run(task="Summarize the content of https://en.wikipedia.org/wiki/Seattle")
    print(result.messages[-1])
                
async def run():
    # Start the server as a subprocess and get stdio read/write functions
    async with stdio_client(server_params) as (read, write):
        # Create a client session to communicate with the server
        async with ClientSession(read, write) as session:
            # Initialize the connection to the server
            await session.initialize()

            # List available tools to confirm what’s there
            response = await session.list_tools()
            tools = response.tools
            print("\nConnected to server with tools:", [tool.name for tool in tools])
            
            #print("\n=== Available Tools ===")
            #for tool in tools:
            #   print(f"- {tool}")
            print("========================\n")
            tools = await mcp_server_tools(server_params)
            print(f"Tools loaded: {tools}")
            # Get a math expression from the user
            #expression = input("Enter a command : ")

            # Call the 'evaluate_expression' tool with the user’s input
            '''
            result = await session.call_tool(
                "get_stock_price",
                arguments={"expression": expression}
            )
            print("\n=== Calculation Result ===")
            print(f"Expression: {expression}")
            print(f"Result: {result}")
            '''
            print("==========================\n")

if __name__ == "__main__":
    # Run the async function
    asyncio.run(run())
    #asyncio.run(main())