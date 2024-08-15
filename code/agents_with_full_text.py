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


# Define data path
base_dir = '../data'
file_paths = {
    'testing_paper': '2024.sdp-1.15.txt',
    'clarity_agent_system_prompts': 'clarity_agent_system_prompts.txt',
    'experiments_methodology_agent_system_prompts': 'experiments_methodology_agent_system_prompts.txt',
    'leader_system_prompts': 'leader_system_prompts.txt',
    'manager_system_prompts': 'manager_system_prompts.txt'
}

full_paths = {key: os.path.join(base_dir, file_name) for key, file_name in file_paths.items()}

# Access individual paths
testing_paper_path = full_paths['testing_paper']
clarity_agent_system_prompts_path = full_paths['clarity_agent_system_prompts']
experiments_methodology_agent_system_prompts_path = full_paths['experiments_methodology_agent_system_prompts']
leader_system_prompts_path = full_paths['leader_system_prompts']
manager_system_prompts_path = full_paths['manager_system_prompts']


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

# list_avail_models()
model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
llm = load_model(model_id)

# Initialize tools
# Set the paper path
# paper_path = Your Path

# A tool that helps agent read files (supposedly)
paper_read_tool = FileReadTool(file_path=testing_paper_path)

# A tool that helps agent do RAG text search (supposedly) 
paper_search_tool = TXTSearchTool(txt = testing_paper_path)



# Define agents
experiments_methodology_agent = Agent(
    role='experiments_methodology_agent',
    goal="Help review a scientific paper, especially focusing the clarity of the paper. Be ready to answer questions from the review_leader and look for answers from the text assigned to you.",
    backstory= f"{experiments_methodology_agent_system_prompts}",
    cache=True,
    llm=llm,
    tools=[paper_read_tool, paper_search_tool],
    
)

clarity_agent = Agent(
    role='clarity_agent',
    goal="Help review a scientific paper, especially the part assigned to you. Be ready to answer questions from the review_leader and look for answers from the text assigned to you.",
    backstory= f"{clarity_agent_system_prompts_path}",
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

# Define the manager agent
manager = Agent(
    role='manager',
    goal="To coordinate and manage the workflow of the review process",
    backstory=f"{manager_system_prompts}",
    cache=True,
    verbose=True,
    llm=llm,
)


# Define high-level Tasks
leader_task = Task(
    description="You can access the paper using 'paper_read_tool' and searching for specific things in the text using 'paper_search_tool' to avoid accessing the whole paper and focus on some specific section of the paper to avoid viewing the paper everytime, which is costly. Task: Write a list of feedback comments, similar to the suggestions a reviewer might make. In addition, focus on major comments rather than minor comments; major comments are important things that affect the overall impact of the paper, whereas minor comments are small things like grammar check. Be specific in your suggestions, including details about method or resource names and any particular steps the authors should follow. However, don't suggest things that are already included/addressed in the paper. Remember that you can collaborate if necessary. If you want to write comments and/or ask for additional ones, you may want to provide your original comments to that the agent knows what was going on. Your review comments should be specific and express an appropriate level of importance. A comment like 'the authors should add more details about the proposed methods, such as XXX' is bad because it is too generic. Even for a paper with a good method description it is always possible to add more details. This review process should follow the high-level plan you have created. Agent information: There are 4 agents in the group, including yourself. You are 'reviewer_leader', the other agents are 'clarity_agent', 'impact_agent', and 'experiments_methodology_agent'.Each agent has a specific focus in the review process, and you should coordinate their efforts to ensure that the review is thorough and comprehensive.",
    expected_output="A final list of feedback comments resembling that of the peer-reviews for scientific papers.",
    agent=reviewer_leader,
)

clarity_agent_tasks = Task(
    description= "You can access the paper using 'paper_read_tool' and searching for specific things in the text using 'paper_search_tool' to avoid accessing the whole paper and focus on some specific section of the paper to avoid viewing the paper everytime, which is costly. Task: Help the reviewer leader by providing information concerning the clarity of the paper.  Informations about agents: There are 4 agents in the group, including yourself. You are 'clarity_agent', the other agents are 'impact_agent', 'experiments_methodology_agent', and 'reviewer_leader'.",
    expected_output="A set of responses to the leaders' requestsd, and feedback on the clarity of the paper.",
    agent= clarity_agent,
    context=[leader_task]
)


impact_agent_tasks = Task(
    description= "You can access the paper using 'paper_read_tool' and searching for specific things in the text using 'paper_search_tool' to avoid accessing the whole paper and focus on some specific section of the paper to avoid viewing the paper everytime, which is costly. Task: Help the reviewer leader by providing information concerning your section of the paper. Informations about agents: There are 4 agents in the group, including yourself. You are 'impact_agent', the other agents are 'clarity_agent', 'experiments_methodology_agent', and 'reviewer_leader'.",
    expected_output="A set of responses to the leaders' requestsd, and feedback on the impact of the paper.",
    agent= impact_agent,
    context=[leader_task]
)

experiments_methodology_tasks = Task(
    description= "You can access the paper using 'paper_read_tool' and searching for specific things in the text using 'paper_search_tool' to avoid accessing the whole paper and focus on some specific section of the paper to avoid viewing the paper everytime, which is costly. Task: Help the reviewer leader by providing information concerning your section of the paper.Informations about agents: There are 4 agents in the group, including yourself. You are 'experiments_methodology_agent', the other agents are 'clarity_agent', 'impact_agent', and 'reviewer_leader'.",
    expected_output="A set of responses to the leaders' requestsd, and feedback on the experiments and methodology of the paper.",
    agent= experiments_methodology_agent,
    context=[leader_task]
)


# Set Crew and kickoff
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
