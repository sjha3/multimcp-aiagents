import asyncio
from fastmcp import Client
import asyncio, json
#from Agents.Agent_with_tools import Agents_with_tools
from autogen_agentchat.ui import Console
from autogen_ext.tools.mcp import mcp_server_tools, StdioServerParams
from Agents.Agent_team import AgentTeam
from dotenv import load_dotenv

class MultiMCPClient:
    """
    A client for connecting to multiple MCP servers.
    This client can be used to interact with various tools exposed by the MCP servers.
    """
    def __init__(self):    
        self.config = json.load(open("mcp-config.json"))
        self.agent_team = AgentTeam(self.config)

    
    async def start_chat(self):
        print("**** Starting chat ****")
        load_dotenv(override=True)  # Load environment variables from .env file
        await self.agent_team.create_team()
        #print(self.tools_)                
        
        while True:
            try:
                task = input("**** Please enter a task: ")
                if task.lower() == "exit":
                    print("**** Exiting chat...")
                    break
                print("Running task:", task)
                await Console(self.agent_team.team.run_stream(task=task))
                
            except Exception as e:
                print(f"Error occurred: {e}")
                break