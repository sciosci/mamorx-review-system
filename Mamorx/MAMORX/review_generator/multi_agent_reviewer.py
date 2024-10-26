from typing import Optional
from langchain_aws import ChatBedrock
from crewai import Agent, Crew, Process
from crewai_tools import TXTSearchTool

from MAMORX.schemas import APIConfigs, MultiAgentPrompt
from MAMORX.custom_crewai.task import CustomTask
from MAMORX.custom_crewai_tools import FileReadToolUTF8, FigureTool, NoveltyTool


class MultiAgentReviewerCrew(object):
    '''
    A Multi Agent Reviewer System build upon crewai
    '''
    def __init__(self, api_config: APIConfigs):
        self.api_config = api_config
        
        # LLM model (ChatBedrock) [Doesn't need to each per each review]
        self.llm: Optional[ChatBedrock] = None

        # Variables that change per each review (different paper or using knowledge or not)
        #   Prompts
        self.prompts = None

        #   Tasks
        self.leader_task: CustomTask = None
        self.clarity_agent_task: CustomTask = None
        self.experiment_agent_task: CustomTask = None
        self.impact_agent_task: CustomTask = None

        #   Tools
        self.paper_read_tool: FileReadToolUTF8 = None
        self.paper_search_tool: TXTSearchTool = None
        self.figure_critic_tool: Optional[FigureTool] = None
        self.novelty_tool: Optional[NoveltyTool] = None

        #   Agents
        self.review_leader: Agent = None
        self.experiment_agent: Agent = None
        self.clarity_agent: Agent = None
        self.impact_agent: Agent = None
        self.manager: Agent = None

        #   Crew
        self.review_crew:Optional[Crew] = None


    
    def setup_tools(self, use_knowledge: bool):
        pass


    def setup_agents(self):
        pass


    def setup_tasks(self):
        pass


    def setup_crew(self):
        pass


    def review_paper(
            self, 
            paper_txt_path: str, 
            novelty_assessment: Optional[str], 
            figure_critic_assessment: Optional[str],
            prompts: MultiAgentPrompt, 
            use_knowledge: bool
        ):
        # Setup Tools

        # Setup Agents

        # Setup Tasks

        # Setup Crew

        # Kickoff Crew
        return ""