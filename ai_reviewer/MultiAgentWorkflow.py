import os
import json
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from model import load_model
from crewai_tools import FileReadTool, TXTSearchTool


class MultiAgentWorkflow:
    def __init__(self, base_dir='data', model_id="anthropic.claude-3-5-sonnet-20240620-v1:0", prompts_file='prompts.json'):
        self.base_dir = base_dir
        self.model_id = model_id
        self.prompts_file = prompts_file
        self.load_environment()
        self.setup_file_paths()
        self.load_file_contents()
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
    
    def setup_file_paths(self):
        file_paths= {
            'testing_paper': '2024.sdp-1.15.txt',
        }

        self.full_paths = {key: os.path.join(self.base_dir, file_name) for key, file_name in file_paths.items()}

    def load_file_contents(self):
        self.file_contents ={}
        for key, path in self.full_paths.items():
            with open(path, 'r') as file:
                with open(path, 'r') as file:
                    self.file_contents[key] = file.read()

    def setup_tools(self):
        self.paper_read_tool = FileReadTool(file_path=self.full_paths['testing_paper'])
        self.paper_search_tool = TXTSearchTool(txt=self.full_paths['testing_paper'])

    def setup_agents(self):
        self.llm = load_model(self.model_id)

        self.review_leader = Agent(
            role='review_leader',
            goal="Lead the review of a scientific paper. Assign tasks to the other agents and answer their questions. Make sure the review is thorough and accurate.",
            backstory=self.prompts['multi_agent_without_knowledge']['leader']['system_prompt'],
            cache=True,
            llm=self.llm,
            tools=[self.paper_read_tool, self.paper_search_tool],
            verbose=True
            )

        self.experiments_agent = Agent(
            role='experiments_agent',
            goal="Help review a scientific paper, especially focusing the experiment/methods of the paper. Be ready to answer questions from the review_leader and look for answers from the text assigned to you.",
            backstory= self.prompts['multi_agent_without_knowledge']['experiment_agent']['system_prompt'],
            cache=True,
            llm=self.llm,
            tools=[self.paper_read_tool, self.paper_search_tool],
            verbose=True,
            )
        
        self.clarity_agent = Agent(
            role='clarity_agent',
            goal="Help review a scientific paper, especially focusing the clarity of the paper. Be ready to answer questions from the review_leader and look for answers from the text assigned to you.",
            backstory=self.prompts['multi_agent_without_knowledge']['clarity_agent']['system_prompt'],
            cache=True,
            llm=self.llm,
            tools=[self.paper_read_tool, self.paper_search_tool],
            verbose=True
            )
        
        self.impact_agent = Agent(
            role='impact_agent',
            goal="Help review a scientific paper, especially focusing the impact of the paper. Be ready to answer questions from the review_leader and look for answers from the text assigned to you.",
            backstory=self.prompts['multi_agent_without_knowledge']['impact_agent']['system_prompt'],
            cache=True,
            llm=self.llm,
            tools=[self.paper_read_tool, self.paper_search_tool],
            verbose=True
            )
        
        self.manager = Agent(
            role='manager',
            goal="Manage the workflow of the review process by bridging the communication between the agents.",
            backstory=self.prompts['multi_agent_without_knowledge']['manager']['system_prompt'],
            cache=True,
            llm=self.llm,
            )

    def setup_tasks(self):
        self.leader_task = Task(
            description=self.prompts['multi_agent_without_knowledge']['leader']['task_prompt'],
            expected_output='A final list of feedbacks/comments for the paper resembling that of the peer-reviews for scientific paper, it should incorporates suggestions from the other expert agents.',
            agent=self.review_leader,
            output_file='aug_21_final_review_2.txt',
            )

        self.clarity_agent_tasks = Task(
            description=self.prompts['multi_agent_without_knowledge']['clarity_agent']['task_prompt'],
            expected_output="A series of messages sent to 'review_leader'.",
            agent=self.clarity_agent,
            context=[self.leader_task]
            )

        self.experiments_agent_tasks = Task(
            description=self.prompts['multi_agent_without_knowledge']['experiment_agent']['task_prompt'],
            expected_output="A series of messages sent to 'review_leader'.",
            agent=self.experiments_agent,
            context=[self.leader_task]
            )

        self.impact_agent_tasks = Task(
            description=self.prompts['multi_agent_without_knowledge']['impact_agent']['task_prompt'],
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

