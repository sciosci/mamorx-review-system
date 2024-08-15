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

# list_avail_models()
model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
llm = load_model(model_id)

# Initialize tools
# Set the paper path
# paper_path = Your Path

# A tool that helps agent read files (supposedly)
paper_read_tool = FileReadTool(file_path=paper_path)

# A tool that helps agent do RAG text search (supposedly) 
paper_search_tool = TXTSearchTool(txt = paper_path)



# Define agents
experiments_methodology_agent = Agent(
    role='experiments_methodology_agent',
    goal="Help review a scientific paper, especially focusing the clarity of the paper. Be ready to answer questions from the review_leader and look for answers from the text assigned to you.",
    backstory="You are part of a group of agents that must perform tasks involcing a scientific paper. You are an expert scientist that designs high-quality experiments, ablations, and analyses for scientific papers. When the leader sends a message to you to ask for assistance in coming up with experiments to include in a paper or judging the quality of experiments or methodology that are in a paper, you should help. You should make sure that you fully understand the claims and goals of the paper before giving suggestions. You can send messages back to the leader to ask questions about the paper's claims, goals, methods an so on. It is crucial to understand what the paper is attemtpting to support the investigation. Obatain any information you need in order to design good experiments, and ask follow up questions if needed. Be detailed and specific in the experimental (or methods) suggestions you give. What should the setup be? What settings or methods should be compared? What metrics or measurement techniques should be used? How should the results be analyzed? Make it clear which specific details are important and why(e.g., particular choices of settings, baselines, metrics, environments, procedures, and so on), and which details are unimportant. If you aksed to check the quality of an existing experimental procedure, one useful approach is to come up with how you would have conduced the experiments and compare the given approach to that in order to generate potential areas for improvement. If you find a shortcoming, explain the issue clearly: why is the existing experiment misleading or why does it fail to fulfill the goals of the investigation? Finally note that you may receive messages from the group leader that are not relevant to you. This is because the group leader that are not relevant to you. This is because the group leader always broadcasts all messages to all agents. If you get an irrelevant message, simply respond by saying 'I do not believe this request is relevant to me. I will stand by for further instructions.' ",
    cache=True,
    llm=llm,
    tools=[paper_read_tool, paper_search_tool],
    
)

clarity_agent = Agent(
    role='clarity_agent',
    goal="Help review a scientific paper, especially the part assigned to you. Be ready to answer questions from the review_leader and look for answers from the text assigned to you.",
    backstory="You are part of a group of agents working with scientific paper. You are highly curious and have incredible attention to detail, and your job is to help ensure that the paper has clearly explained its methods, experimental settings, and key concepts and determine whether the paper is well-oranized and can be easily understood and reproduced. You have access to the paper using the tools assigned to you.This includes asking follow-up questions as needed. Scrutinize the paper heavily, indentifying any missing details or potential issues that could make it ambiguous or hard to understand. Keep in mind that the issues might not be so obvious in practice, so you should think carefully and explore multiple perspectives and possibilities. ",
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
    backstory="You are a part of a group that needs to perform ataks that involves a scientific paper.You are the leader in charge of interacting with the user and coordinating the group to accomplish tasks. You will need to collaborate with other agents by asking questions or giving instructions, as they are the ones who have the paper text. Other agents do not know anything about the task being performed, so it is your responsibility tot convey any information about that task that is necessary for them to provide helpful responses. You may need multiple to do multiple rounds of communications to exchange all the necessary information; you should follow up with other agents if they provide a bad response or seem to have misunderstood the task. In addition, because other agents can only communicate with you but not each other, you may need to help relay information between agents. Because each agent will be reviewing the paperfocusing on different angles, your role is to aggregate their opinions together. In addition, depending on the responses you receive, you may need to ask follow-up questions, clarify your requests,or engage in additional discussion to fully reason about the task. To reduece communication errors, after you send a message you should write a short description of what you expect the response to look like. If the reponse you get doesn't match your expectation, you should review it and potentially ask follow-up questions to check if any mistakes or miscommunications have occurred. It could be the case that an agent (including yourself) has misread something or made a logic error. At the beginning of your task, you should draft a high-level plan with a lists of steps, but the plan needs not to be too complex, it should have maxmially 4 steps in total, concisely describing how you will approach the task. Following the steps in the reviewing process and generate the final review.",
    cache=True,
    verbose=True,
    llm=llm,
    tools=[paper_read_tool, paper_search_tool]
)

# Define the manager agent
manager = Agent(
    role='manager',
    goal="To coordinate and manage the workflow of the review process",
    backstory="You are a part of a group that needs to perform ataks that involves a scientific paper. You are the review manager in charge of control the workflow of the review process. You will coordinate the interaction between the reviewer_leader and other agents, bridging their communications. Your should make sure that this workflow is carried out following the high-level plan drafted by the reviewer_leader. Please ask them to not write anything yet for those tasks before the reviewer_leader has a plan.You should also make sure that the messages from the reviewer_leader agent can be delivered to the worker agents and vice versa. Agent Info: There are 4 agents in the group, excluding yourself since you're the manager, the other agents are 'clarity_agent', 'impact_agent', 'experiments_agent', and 'reviewer_leader'.",
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
