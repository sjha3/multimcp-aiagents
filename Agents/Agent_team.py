'''
This module defines the AgentTeam class, which manages a collection of agents.
It will be responsible for creating a team of agents and managing their interactions.
'''
from Agents.Agent_with_tools import Agent_with_tools
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.messages import AgentEvent, ChatMessage
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.ui import Console
from typing import Sequence
import os, traceback
from dotenv import load_dotenv

class AgentTeam:
    def __init__(self, mcp_config):
        self.team = None
        self.mcp_config = mcp_config
        self.agents = []
        load_dotenv(override=True)  # Load environment variables from .env file
        self.model_client = AzureOpenAIChatCompletionClient(
            azure_endpoint=os.getenv("azure_endpoint"),
            azure_deployment=os.getenv("azure_deployment"),
            api_version=os.getenv("api_version"),
            api_key=os.getenv("api_key"),
            model= "gpt-4o-2024-11-20"#enhance token/cost estimation using it instead of gpt-4o  
        )
        
        
    async def create_team(self):
        print("**** Creating agent team with tools from MCP servers ****")
        for server in self.mcp_config["mcpServers"].values():
            print(f"Server command: {server['name']}, {server['command']}, args: {server['args']}, env: {server.get('env', {})}")
            agent_tool = Agent_with_tools(server, self.model_client)
            await agent_tool.create_agent()
            if agent_tool.agent is not None:
                self.agents.append(agent_tool.agent)
        
        response_agent = AssistantAgent(
            name="ResponseAgent",
            description="An agent that formats and sends the final response to the user.",
            model_client=self.model_client,
            system_message="""You are a response agent. 
            Your task is to format and send the final response to the user.
            Always end the conversation with 'TERMINATE'.
            
            Always end your response with 'TERMINATE' to indicate the conversation is complete.
            """,
        )
        
        planning_agent = AssistantAgent(
            "PlanningAgent",
            model_client=self.model_client,
            description="""
                An agent that plans tasks based on user requests.
                It should break down tasks and delegate them to appropriate agents.
                """,
            system_message=
                """
                    You are a planning agent. 
                    Your task is to break down user requests into smaller tasks and delegate them to appropriate agents.
                    Your team members are
                    - StockPortfolioManager: Manager of stock portfolio in robinhood.
                    - ReviewAgent: Manages review objects.   
                    - HotelSearchAgent : Use it to search for hotels only.
                    - WebSearch : Use it to perform web searches.
                    - PlaywrightAgent: Performs web automation tasks using Playwright.                
                    - ResponseAgent: Responsible for responding to the user with the final response.
                    
                    You only plan and delegate tasks, you do not execute them.
                    
                    When assignning tasks to agents, use the following format:
                    1. <agent>: <task>
                    
                    Once a task is completed by another agent, delegate the response to the **ResponseAgent**
                    to format and send the final response to the user.
                """,
        )
        
        

        self.agents.append(planning_agent)
        self.agents.append(response_agent)
        print("**** All Agents created successfully ****", self.agents)
        
        text_mention_termination = TextMentionTermination("TERMINATE")
        max_messages_termination = MaxMessageTermination(25)
        termination = text_mention_termination | max_messages_termination
            
        def selector_func(messages: Sequence[AgentEvent | ChatMessage]) -> str | None:
            if messages[-1].source != planning_agent.name:
                return planning_agent.name
            return None
        
        self.team = SelectorGroupChat(self.agents,
                                 model_client=self.model_client, 
                                 selector_func=selector_func,
                                 termination_condition=termination,
                                 allow_repeated_speaker=True)
        print("**** Agent team created successfully ****")