import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from model import load_model, list_avail_models
from crewai_tools import FileReadTool
from crewai_tools import TXTSearchTool

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
os.environ['OPENAI_MODEL_NAME'] = os.getenv('OPENAI_MODEL_NAME')
os.environ['BROWSERBASE_API_KEY'] = 'BROWSERBASE_API_KEY'
os.environ['BROWSERBASE_PROJECT_ID'] = 'BROWSERBASE_PROJECT_ID'
os.environ['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID')
os.environ['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY')
os.environ['AWS_DEFAULT_REGION'] = os.getenv('AWS_DEFAULT_REGION')


# Define paths
base_dir = 'data'
file_paths = {
    'testing_paper': '2024.sdp-1.15.txt',
    'clarity_agent_system_prompts': 'clarity_agent_system_prompts.txt',
    'experiments_methodology_agent_system_prompts': 'experiments_methodology_agent_system_prompts.txt',
    'leader_system_prompts': 'leader_system_prompts.txt',
    'manager_system_prompts': 'manager_system_prompts.txt',
    'leader_task_prompts': 'leader_task_prompts.txt',
}

full_paths = {key: os.path.join(base_dir, file_name) for key, file_name in file_paths.items()}

# Access individual paths
testing_paper_path = full_paths['testing_paper']
clarity_agent_system_prompts_path = full_paths['clarity_agent_system_prompts']
experiments_methodology_agent_system_prompts_path = full_paths['experiments_methodology_agent_system_prompts']
leader_system_prompts_path = full_paths['leader_system_prompts']
manager_system_prompts_path = full_paths['manager_system_prompts']
leader_task_prompts_path = full_paths['leader_task_prompts']

# Read files
def read_files(paths):
    contents = {}
    for key, path in paths.items():
        with open(path, 'r') as file:
            contents[key] = file.read()
    return contents

file_contents = read_files(full_paths)

# Access the contents
testing_paper = file_contents['testing_paper']
clarity_agent_system_prompts = file_contents['clarity_agent_system_prompts']
experiments_methodology_agent_system_prompts= file_contents['experiments_methodology_agent_system_prompts']
leader_system_prompts = file_contents['leader_system_prompts']
manager_system_prompts = file_contents['manager_system_prompts']
leader_task_prompts = file_contents['leader_task_prompts']

# list_avail_models()
model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
llm = load_model(model_id)

# Initialize tools
paper_path = os.path.abspath("/Users/harry/Desktop/SOS/agent/crew_ai_agent_project/daniel_2024_paper.txt")
paper_read_tool = FileReadTool(file_path=testing_paper_path)
paper_search_tool = TXTSearchTool(txt = testing_paper_path)



experiments_methodology_agent = Agent(
    role='experiments_methodology_agent',
    goal="Help review a scientific paper, especially focusing the clarity of the paper. Be ready to answer questions from the review_leader and look for answers from the text assigned to you.",
    backstory=f"{experiments_methodology_agent_system_prompts}",
    cache=True,
    llm=llm,
    tools=[paper_read_tool, paper_search_tool],
)

clarity_agent = Agent(
    role='clarity_agent',
    goal="Help review a scientific paper, especially the part assigned to you. Be ready to answer questions from the review_leader and look for answers from the text assigned to you.",
    backstory= f"{clarity_agent_system_prompts}",
    cache=True,
    llm=llm,
    tools=[paper_read_tool, paper_search_tool],
    
)

impact_agent = Agent(
    role='impact_agent',
    goal="Help review a scientific paper, especially focusing on the impact of the paper. Be ready to answer questions from the review_leader and look for answers from the text assigned to you.",
    backstory="You are part of a group of agents working with scientific paper. You need to pay attention the the potential impacts of the paper.",
    cache=True,
    llm=llm,
    tools=[paper_read_tool, paper_search_tool],
)

reviewer_leader = Agent(
    role='reviewer_leader',
    goal="To orchestrate and write peer-review style comments for a scientific paper as a peer-reviewer would. (Paper not written by you)",
    backstory=f"{leader_system_prompts}",
    cache=True,
    verbose=True,
    llm=llm,
    tools=[paper_read_tool, paper_search_tool]
)

manager = Agent(
    role='manager',
    goal="To coordinate and manage the workflow of the review process, help agents coomunicate by sending the responses from the agents to the reviewer_leader or other agents.",
    backstory=f"{manager_system_prompts}",
    cache=True,
    verbose=True,
    llm=llm,
)

leader_task = Task(
    description=f"{leader_task_prompts}",
    expected_output="A final feedback comments resembling that of the peer-reviews for scientific papers, achieved by aggregating the comments from other agents.",
    agent=reviewer_leader,
    output_file="final_review.txt",
)

clarity_agent_tasks = Task(
    description= "Task: Help the reviewer leader by writing feedbacks on the clarity of the paper. If the reviewer_leader ask you questions, you will also need to respond to the questions.  Informations about agents: There are 4 agents in the group, including yourself. You are 'clarity_agent', the other agents are 'impact_agent', 'experiments_methodology_agent', and 'reviewer_leader'. You can access the paper using 'paper_read_tool' and searching for specific things in the text using 'paper_search_tool' to avoid accessing the whole paper and focus on some specific section of the paper to avoid viewing the paper everytime, which is costly. Please don't message others agents a chunk of the paper as they will have means to locate relevant content in the paper. ",
    expected_output="A series of messages to 'reviewer_leader', and eventually a list of feedback focused on the clarity of the paper.",
    agent= clarity_agent,
    context=[leader_task]
)


impact_agent_tasks = Task(
    description= "Task: Help the reviewer leader by writing feedback on the impact of the paper. Informations about agents: There are 4 agents in the group, including yourself. You are 'impact_agent', the other agents are 'clarity_agent', 'experiments_methodology_agent', and 'reviewer_leader'. You can access the paper using 'paper_read_tool' and searching for specific things in the text using 'paper_search_tool' to avoid accessing the whole paper and focus on some specific section of the paper to avoid viewing the paper everytime, which is costly. ",
    expected_output="A series of messages to 'reviewer_leader', and eventually  list of feedback focused on the impact of the paper",
    agent= impact_agent,
    context=[leader_task]
)

experiments_methodology_tasks = Task(
    description= "Task: Help the reviewer leader by wrtting feedbacks on the experiments_methodology of the paper. Informations about agents: There are 4 agents in the group, including yourself. You are 'experiments_methodology_agent', the other agents are 'clarity_agent', 'impact_agent', and 'reviewer_leader'. You can access the paper using 'paper_read_tool' and searching for specific things in the text using 'paper_search_tool' to avoid accessing the whole paper and focus on some specific section of the paper to avoid viewing the paper everytime, which is costly. ",
    expected_output="A series of messages to 'reviewer_leader', and eventually a list of feedback focused on the experiments/methodology of the paper.",
    agent= experiments_methodology_agent,
    context=[leader_task]
)


review_crew = Crew(
    tasks=[leader_task, clarity_agent_tasks, impact_agent_tasks, experiments_methodology_tasks],
    agents=[impact_agent,reviewer_leader, experiments_methodology_agent, clarity_agent],
    # manager_llm=ChatOpenAI(temperature=0, model='gpt-4o-mini'),
    process=Process.hierarchical,
    memory=True,
    manager_agent=manager,
    # planning=True,
    # planning_llm=ChatOpenAI(model="gpt-4o"),
)

result = review_crew.kickoff()

print(result)
