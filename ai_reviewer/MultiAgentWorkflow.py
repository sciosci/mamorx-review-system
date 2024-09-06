import os
import json
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from model import load_model
from crewai_tools import FileReadTool, TXTSearchTool, BaseTool,tool


class MultiAgentWorkflow:
    def __init__(self, base_dir, model_id, text_file=None, output_path=None,prompts_file=None, novelty_assessment_path=None, figure_critic_assessment_path=None, system_type=None):
        self.base_dir = base_dir
        self.model_id = model_id
        self.system_type = system_type
        self.output_path = output_path
        self.text_file = text_file
        self.prompts_file = prompts_file
        self.novelty_assessment = novelty_assessment_path
        self.figure_critic_assessment = figure_critic_assessment_path
        self.load_environment()
        self.load_prompts()
        self.setup_tools()
        self.setup_agents()
        self.setup_tasks()
        self.setup_crew()

    def load_environment(self):
        load_dotenv()
        env_vars = ['OPENAI_API_KEY', 'OPENAI_MODEL_NAME', 'BROWSERBASE_PROJECT_ID', 
                    'AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY', 'AWS_DEFAULT_REGION'
        ]
        for var in env_vars:
            os.environ[var] = os.getenv(var, '')

    def load_prompts(self):
        with open(self.prompts_file, 'r') as file:
            self.prompts = json.load(file)


    def setup_tools(self):
        self.paper_read_tool = FileReadTool(self.text_file)
        self.paper_search_tool = TXTSearchTool(text=self.text_file)
        if (self.system_type == 'multi_agent_with_knowledge'):
            self.figure_critic_tool = FileReadTool(self.figure_critic_assessment)
            self.novelty_tool = FileReadTool(self.novelty_assessment)
        else:
            self.figure_critic_tool = None
            self.novelty_tool = None


    def setup_agents(self):
        self.llm = load_model(self.model_id)

        common_tools = [self.paper_read_tool, self.paper_search_tool]

        self.review_leader = Agent(
            role='review_leader',
            goal="Lead the review of a scientific paper. Assign tasks to the other agents and answer their questions. Make sure the review is thorough and accurate.",
            backstory=self.prompts[self.system_type]['leader']['system_prompt'],
            cache=True,
            llm=self.llm,
            tools=common_tools + ([self.figure_critic_assessment, self.novelty_tool] if self.system_type == 'multi_agent_with_knowledge' else []),
            verbose=True
            )

        self.experiments_agent = Agent(
            role='experiments_agent',
            goal="Help review a scientific paper, especially focusing the experiment/methods of the paper. Be ready to answer questions from the review_leader and look for answers from the text assigned to you.",
            backstory= self.prompts[self.system_type]['experiment_agent']['system_prompt'],
            cache=True,
            llm=self.llm,
            tools=common_tools + ([self.figure_critic_assessment] if self.system_type == 'multi_agent_with_knowledge' else []),
            verbose=True,
            )
        
        self.clarity_agent = Agent(
            role='clarity_agent',
            goal="Help review a scientific paper, especially focusing the clarity of the paper. Be ready to answer questions from the review_leader and look for answers from the text assigned to you.",
            backstory=self.prompts[self.system_type]['clarity_agent']['system_prompt'],
            cache=True,
            llm=self.llm,
            tools=common_tools + ([self.figure_critic_assessment] if self.system_type == 'multi_agent_with_knowledge' else []),
            verbose=True
            )
        
        self.impact_agent = Agent(
            role='impact_agent',
            goal="Help review a scientific paper, especially focusing the impact of the paper. Be ready to answer questions from the review_leader and look for answers from the text assigned to you.",
            backstory=self.prompts[self.system_type]['impact_agent']['system_prompt'],
            cache=True,
            llm=self.llm,
            tools=common_tools + ([self.novelty_tool] if self.system_type == 'multi_agent_with_knowledge' else []),
            verbose=True
            )
        
        self.manager = Agent(
            role='manager',
            goal="Manage the workflow of the review process by bridging the communication between the agents.",
            backstory=self.prompts[self.system_type]['manager']['system_prompt'],
            cache=True,
            llm=self.llm,
            )

    def setup_tasks(self):
        self.leader_task = Task(
            description=self.prompts[self.system_type]['leader']['task_prompt'],
            expected_output='A final list of comprehensive feedbacks/comments for the paper resembling that of the peer-reviews for scientific paper, it should incorporates suggestions from the other expert agents.',
            agent=self.review_leader,
            output_file= self.output_path
            )

        self.clarity_agent_tasks = Task(
            description=self.prompts['multi_agent_with_knowledge']['clarity_agent']['task_prompt'],
            expected_output="A series of messages sent to 'review_leader'.",
            agent=self.clarity_agent,
            context=[self.leader_task]
            )

        self.experiments_agent_tasks = Task(
            description=self.prompts['multi_agent_with_knowledge']['experiment_agent']['task_prompt'],
            expected_output="A series of messages sent to 'review_leader'.",
            agent=self.experiments_agent,
            context=[self.leader_task]
            )

        self.impact_agent_tasks = Task(
            description=self.prompts['multi_agent_with_knowledge']['impact_agent']['task_prompt'],
            expected_output="A series of messages sent to 'review_leader'.",
            agent=self.impact_agent,
            context=[self.leader_task]
            )
            

        
    def setup_crew(self):
        self.review_crew = Crew(
            agents=[self.review_leader, self.experiments_agent, self.clarity_agent, self.impact_agent],
            tasks=[self.leader_task, self.clarity_agent_tasks, self.experiments_agent_tasks, self.impact_agent_tasks],
            process=Process.hierarchical,
            memory=True,
            manager_agent=self.manager
            )

    def initiate_workflow(self):
        self.review_crew.kickoff()

