import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from model import load_model
from crewai_tools import FileReadTool, TXTSearchTool
from SemanticScholar import SemanticScholar


class MultiAgentWorkflow:
    def __init__(self, base_dir='data', model_id="anthropic.claude-3-5-sonnet-20240620-v1:0"):
        self.base_dir = base_dir
        self.model_id = model_id
        self.load_environment()
        self.setup_file_paths()
        self.load_file_contents()
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
    
    def setup_file_paths(self):
        file_paths= {
            'testing_paper': '2024.sdp-1.15.txt',
            'clarity_agent_system_prompts': 'clarity_agent_system_prompts.txt',
            'experiments_methodology_agent_system_prompts': 'experiments_methodology_agent_system_prompts.txt',
            'leader_system_prompts': 'leader_system_prompts.txt',
            'manager_system_prompts': 'manager_system_prompts.txt',
            'leader_task_prompts': 'leader_task_prompts.txt',
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
        self.related_paper_tool = SemanticScholar()

    def setup_agents(self):
        self.llm = load_model(self.model_id)

        self.review_leader = Agent(
            role='review_leader',
            goal="Lead the review of a scientific paper. Assign tasks to the other agents and answer their questions. Make sure the review is thorough and accurate.",
            backstory=self.file_contents['leader_system_prompts'],
            cache=True,
            llm=self.llm,
            tools=[self.paper_read_tool, self.paper_search_tool],
            )

        self.experiments_methodology_agent = Agent(
            role='experiments_methodology_agent',
            goal="Help review a scientific paper, especially focusing the clarity of the paper. Be ready to answer questions from the review_leader and look for answers from the text assigned to you.",
            backstory=self.file_contents['experiments_methodology_agent_system_prompts'],
            cache=True,
            llm=self.llm,
            tools=[self.paper_read_tool, self.paper_search_tool],
            )
        
        self.clarity_agent = Agent(
            role='clarity_agent',
            goal="Help review a scientific paper, especially focusing the clarity of the paper. Be ready to answer questions from the review_leader and look for answers from the text assigned to you.",
            backstory=self.file_contents['clarity_agent_system_prompts'],
            cache=True,
            llm=self.llm,
            tools=[self.paper_read_tool, self.paper_search_tool],
            )
        
        self.novelty_agent = Agent(
            role='novelty_agent',
            goal="Help review a scientific paper, especially focusing the novelty of the paper. Be ready to answer questions from the review_leader and look for answers from the text assigned to you.",
            backstory=self.file_contents['impact_system_prompts'],
            cache=True,
            llm=self.llm,
            tools=[self.paper_read_tool, self.paper_search_tool, self.related_paper_tool],
            )
        
        self.manager = Agent(
            role='manager',
            goal="Help review a scientific paper, especially focusing the clarity of the paper. Be ready to answer questions from the review_leader and look for answers from the text assigned to you.",
            backstory=self.file_contents['manager_system_prompts'],
            cache=True,
            llm=self.llm,
            tools=[self.paper_read_tool, self.paper_search_tool],
            )
        

        def setup_tasks(self):
            self.leader_task = Task(
                description=self.file_contents['leader_task_prompts'],
                expected_output='A set of messgages to other agents to orchestrate the review and a final feedback comments resembling that of the peer-reviews for scientific paper.',
                agent=self.review_leader,
                output_file='final_review.txt',
            )

            self.clarity_agent_tasks = Task(
                description=self.file_contents['clarity_agent_task_prompts'],
                expected_output="A series of messages to 'reviewer_leader', and eventually a list of feedback focused on the clarity of the paper.",
                agent=self.clarity_agent,
                output_file="clarity_feedback.txt",
            )

            self.experiments_methodology_agent_tasks = Task(
                description=self.file_contents['experiments_methodology_agent_task_prompts'],
                expected_output="A series of messages to 'reviewer_leader', and eventually a list of feedback focused on the methodology of the paper.",
                agent=self.experiments_methodology_agent,
                output_file="experiments_methodology_feedback.txt",
            )

            self.impact_agent_tasks = Task(
                description=self.file_contents['impact_system_prompts'],
                expected_output="A series of messages to 'reviewer_leader', and eventually a list of feedback focused on the impact of the paper.",
                agent=self.impact_agent,
                output_file="impact_feedback.txt",
            )
            

        
        def setup_crews(self):
            self.review_crew = Crew(
                agents=[self.review_leader, self.experiments_methodology_agent, self.clarity_agent, self.impact_agent, self.manager],
                takss=[self.leader_task, self.clarity_agent_tasks, self.experiments_methodology_agent_tasks, self.impact_agent_tasks],
                process=Process.hierarchical,
                memory=True,
                manager_agent=self.manager,

            )

        def initiate_workflow(self):
            result = self.review_crew.kickoff()
            return result

