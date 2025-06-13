import asyncio,sys
#from localmcpclient.client import MCPClient
from multiple_server_client import MultiMCPClient

#from Agents import review_agent, finance_agent

async def main():
    client = MultiMCPClient()    
    try: 
        await client.start_chat()
    except Exception as e:
        print(f"Error connecting to server: {e}")


    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except asyncio.CancelledError:
        print("Asyncio task was cancelled during shutdown.")
        sys.exit(1)
    except RuntimeError as e:
        print(f"Runtime error during asyncio shutdown: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unhandled exception during shutdown: {e}")
        sys.exit(1)