import os
from typing import Optional
from crewai import Agent, Crew, Process
from crewai_tools import TXTSearchTool


from MAMORX.schemas import APIConfigs, MultiAgentPrompt, MultiAgentCrewReviewResult
from MAMORX.custom_crewai.task import CustomTask
from MAMORX.custom_crewai_tools import FileReadToolUTF8, TextContainerTool
from MAMORX.custom_crewai_tools.figure_tool import FigureTool
from MAMORX.custom_crewai_tools.novelty_tool import NoveltyTool
from MAMORX.utils import load_chatbedrock_llm_model


class MultiAgentReviewerCrew(object):
    '''
    A Multi Agent Reviewer System build upon crewai
    '''
    def __init__(self, api_config: APIConfigs):
        self.api_config = api_config
        self.llm = load_chatbedrock_llm_model(api_config)
        

        # Setup environment variables for anthropic bedrock
        # ,
        #     region=api_config["aws_default_region"]
        # os.environ['LITELLM_LOG'] = 'DEBUG'

        # self.llm = LLM(
        #     model=api_config['anthropic_model_id'],
        #     aws_access_key_id=api_config['aws_access_key_id'],
        #     aws_secret_access_key=api_config['aws_secret_access_key'],
        #     aws_region_name=api_config['aws_default_region']
        # )
        # self.llm = LLM(
        #     model="ollama/llama3.1:70b", 
        #     base_url="http://localhost:11434"
        # )
        # self.llm = Client(host="http://localhost:11434")
        # os.environ['LITELLM_LOG'] = 'DEBUG'


    def review_paper(
            self, 
            paper_txt_path: str, 
            novelty_assessment: Optional[str], 
            figure_critic_assessment: Optional[str],
            prompts: MultiAgentPrompt, 
            use_knowledge: bool,
            output_path: str
        ) -> MultiAgentCrewReviewResult:
        #   Tools
        paper_read_tool: FileReadToolUTF8 = FileReadToolUTF8(paper_txt_path)

        # Setup OPENAI_API_KEY as environment variable for TXTSearchTool
        os.environ["OPENAI_API_KEY"] = self.api_config["openai_api_key"]
        paper_search_tool: TXTSearchTool = TXTSearchTool(txt=str(paper_txt_path))
        novelty_tool: Optional[NoveltyTool] = NoveltyTool(content=novelty_assessment)
        figure_critic_tool: Optional[FigureTool] = FigureTool(content=figure_critic_assessment)

        common_agent_tools = [paper_read_tool, paper_search_tool]

        #   Agents
        review_leader: Agent = Agent(
            role='review_leader',
            goal="Lead the review of a scientific paper. Assign tasks to the other agents and answer their questions. Make sure the review is thorough and accurate.",
            backstory=prompts['leader']['system_prompt'],
            cache=True,
            llm=self.llm,
            tools=common_agent_tools + ([figure_critic_tool, novelty_tool] if use_knowledge else []),
            verbose=True,
            debug_mode=True
            )
        experiments_agent: Agent = Agent(
            role='experiments_agent',
            goal="Help review a scientific paper, especially focusing the experiment/methods of the paper. Be ready to answer questions from the review_leader and look for answers from the text assigned to you.",
            backstory=prompts['experiment_agent']['system_prompt'],
            cache=True,
            llm=self.llm,
            tools=common_agent_tools + ([figure_critic_tool] if use_knowledge else []),
            verbose=True,
            debug_mode=True
            )
        clarity_agent: Agent = Agent(
            role='clarity_agent',
            goal="Help review a scientific paper, especially focusing the clarity of the paper. Be ready to answer questions from the review_leader and look for answers from the text assigned to you.",
            backstory=prompts['clarity_agent']['system_prompt'],
            cache=True,
            llm=self.llm,
            tools=common_agent_tools + ([figure_critic_tool] if use_knowledge else []),
            verbose=True,
            debug_mode=True
            )
        impact_agent: Agent = Agent(
            role='impact_agent',
            goal="Help review a scientific paper, especially focusing the impact of the paper. Be ready to answer questions from the review_leader and look for answers from the text assigned to you.",
            backstory=prompts['impact_agent']['system_prompt'],
            cache=True,
            llm=self.llm,
            tools=common_agent_tools + ([novelty_tool] if use_knowledge else []),
            verbose=True,
            debug_mode=True
            )
        manager: Agent = Agent(
            role='manager',
            goal="Manage the workflow of the review process by bridging the communication between the agents.",
            backstory=prompts['manager']['system_prompt'],
            cache=True,
            llm=self.llm,
            debug_mode=True,
            allow_delegation=True
            )

        #  Tasks
        leader_task: CustomTask = CustomTask(
            description=prompts['leader']['task_prompt'],
            expected_output='A final review for the paper resembling that of the peer-reviews for scientific paper, it should be a very detailed and honest discussion of the paper.',
            agent=review_leader,
            output_file= output_path
            )
        clarity_agent_tasks: CustomTask = CustomTask(
            description=prompts['clarity_agent']['task_prompt'],
            expected_output="A series of messages sent to 'review_leader'.",
            agent=clarity_agent,
            context=[leader_task]
            )
        experiments_agent_tasks: CustomTask = CustomTask(
            description=prompts['experiment_agent']['task_prompt'],
            expected_output="A series of messages sent to 'review_leader'.",
            agent=experiments_agent,
            context=[leader_task]
            )

        impact_agent_tasks: CustomTask = CustomTask(
            description=prompts['impact_agent']['task_prompt'],
            expected_output="A series of messages sent to 'review_leader'.",
            agent=impact_agent,
            context=[leader_task]
            )

        #   Crew
        review_crew:Optional[Crew] = Crew(
            agents=[review_leader, experiments_agent, clarity_agent, impact_agent],
            tasks=[leader_task, clarity_agent_tasks, experiments_agent_tasks, impact_agent_tasks],
            process=Process.hierarchical,
            memory=True,
            manager_agent=manager
            )

        # Kickoff Crew
        crew_output = review_crew.kickoff()

        # Load review from output file
        with open(output_path, "r") as f:
            generated_review = f.read()

        final_result = MultiAgentCrewReviewResult(
            crew=review_crew,
            crew_output=crew_output,
            review=generated_review,
            usage_metrics=review_crew.usage_metrics
        )
        print(review_crew.usage_metrics, end="\n\n")

        return final_result