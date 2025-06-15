from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools
from autogen_agentchat.agents import AssistantAgent
from autogen_core import CancellationToken
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
import os, traceback
from dotenv import load_dotenv
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.messages import AgentEvent, ChatMessage
from autogen_agentchat.ui import Console
from typing import Sequence
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

'''
This module will simply create an agent with tools exposed by the MCP servers.
'''
class Agent_with_tools():
    
    def __init__(self, mcp_server_config:dict, model_client: AzureOpenAIChatCompletionClient):
        self.server_config = mcp_server_config
        self.tools = []
        self.model_client = model_client
        self.agent = None

    async def create_agent(self):
        print("**** Create agent :  ****", self.server_config["name"])
        text_mention_termination = TextMentionTermination("TERMINATE")
        max_messages_termination = MaxMessageTermination(25)
        termination = text_mention_termination | max_messages_termination
        try:
            server_params_autogen = StdioServerParams(
                    command=self.server_config["command"],
                    args=self.server_config["args"],
                    env=self.server_config["env"],
                    read_timeout_seconds=30
            )
            self.tools = await mcp_server_tools(server_params_autogen)
            self.agent = AssistantAgent(
                name = self.server_config["name"],
                model_client = self.model_client,
                system_message= self.server_config["system_message"],
                tools = self.tools
            )
            print("**** Created agent :  ****", self.server_config["name"])            
        
        except Exception as e:
            print(f"Error creating agent: {self.server_config} \n {e}")
            traceback.print_exc()
            return None
        
        
        
        
        