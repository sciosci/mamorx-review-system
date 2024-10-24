import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from model import load_model, list_avail_models
from crewai_tools import FileReadTool, TXTSearchTool
from SemanticScholar import SemanticScholar

load_dotenv()
# os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
# os.environ['OPENAI_MODEL_NAME'] = os.getenv('OPENAI_MODEL_NAME')
# os.environ['BROWSERBASE_API_KEY'] = 'BROWSERBASE_API_KEY'
# os.environ['BROWSERBASE_PROJECT_ID'] = 'BROWSERBASE_PROJECT_ID'
# os.environ['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID')
# os.environ['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY')
# os.environ['AWS_DEFAULT_REGION'] = os.getenv('AWS_DEFAULT_REGION')

# list_avail_models()
model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
llm = load_model(model_id)


# Initialize tools
paper_path = "../data/daniel_2024_paper.txt"
paper_read_tool = FileReadTool(file_path=paper_path)
paper_search_tool = TXTSearchTool(txt = paper_path)
ss_tool = SemanticScholar()



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

# impact_agent = Agent(
#     role='impact_agent',
#     goal="Help review a scientific paper, especially focusing on the impact of the paper. Be ready to answer questions from the review_leader and look for answers from the text assigned to you.",
#     backstory="You are part of a group of agents working with scientific paper. You need to pay attention the the potential impacts of the paper.",
#     cache=True,
#     llm=llm,
#     tools=[paper_read_tool, paper_search_tool],
    
# )

novelty_agent = Agent(
    role='novalty_agent',
    goal="Review the novelty of this paper based on the information given by the leader agent, and provide feedback to the leader agent.",
    backstory="""
        You are part of a group of agents that must perform tasks involving a scientific paper. 
        You are a knowledgeable and experienced scientist tasked with reviewing the novelty and impact of a scientific paper.
        When the leader sends a message to you to ask for assistance in evaluating the novelty and impact of a paper, you should help. 
        you should ensure that you fully understand the context. Carefully read information about the paper’s abstract, introduction, and 
        conclusion to fully grasp the research’s objectives, methods, and findings.	Consider the current state of research in the field and 
        how the paper fits within that context. To evaluate novelty, you should assess the originality of the research question or hypothesis. 
        Is the problem or topic being addressed new or unique? Examine the methods and approaches used in the study. Are they innovative or do 
        they represent a significant advancement over existing techniques? Consider whether the results or findings provide new insights or open 
        up new avenues for further research. You can retrieve the related papers with provided tools. Use these papers to better understand the 
        context in this area and the breakthrough this paper made.
        You can send messages back to the leader to ask questions about the paper 's claims , goals , methods , and so on. 
      	You should provide a critical analysis including
	    •	Highlight the strengths and weaknesses of the paper regarding its novelty and impact.
	    •	Suggest ways the paper could be improved to enhance its contribution to the field.
	    •	Provide a balanced assessment that acknowledges both the potential limitations and the strengths of the study.
	    Conclude with an overall evaluation at final. Summarize your assessment by stating your overall impression of the 
        paper’s novelty and impact.
        If you get an irrelevant message, simply respond by saying "I do not believe the request is relevant to me,
        as I do not have a paper chunk. I will stand by for further instructions."
    """,
    llm=llm,
    tool=[ss_tool,paper_read_tool, paper_search_tool]
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


# impact_agent_tasks = Task(
#     description= "You can access the paper using 'paper_read_tool', search for abstracts of related papers with 'ss_tool' and search for specific things in the text using 'paper_search_tool' to avoid accessing the whole paper and focus on some specific section of the paper to avoid viewing the paper everytime, which is costly. Task: Help the reviewer leader by providing information concerning your section of the paper. Informations about agents: There are 4 agents in the group, including yourself. You are 'impact_agent', the other agents are 'clarity_agent', 'experiments_methodology_agent', and 'reviewer_leader'.",
#     expected_output="A set of responses to the leaders' requestsd, and feedback on the impact of the paper.",
#     agent= novelty_expert,
#     context=[leader_task],
# )

novelty_agent_tasks = Task(
    description= "You can access the paper using 'paper_read_tool', search for abstracts of related papers with 'ss_tool' and search for specific things in the text using 'paper_search_tool' to avoid accessing the whole paper and focus on some specific section of the paper to avoid viewing the paper everytime, which is costly. Task: Help the reviewer leader by providing information concerning your section of the paper. Informations about agents: There are 4 agents in the group, including yourself. You are 'novelty_agent', the other agents are 'clarity_agent', 'experiments_methodology_agent', and 'reviewer_leader'.",
    expected_output="A set of responses to the leaders' requestsd, and feedback on the impact of the paper.",
    agent= novelty_agent,
    context=[leader_task],
)


experiments_methodology_tasks = Task(
    description= "Task: Help the reviewer leader by wrtting feedbacks on the experiments_methodology of the paper. Informations about agents: There are 4 agents in the group, including yourself. You are 'experiments_methodology_agent', the other agents are 'clarity_agent', 'impact_agent', and 'reviewer_leader'. You can access the paper using 'paper_read_tool' and searching for specific things in the text using 'paper_search_tool' to avoid accessing the whole paper and focus on some specific section of the paper to avoid viewing the paper everytime, which is costly. ",
    expected_output="A series of messages to 'reviewer_leader', and eventually a list of feedback focused on the experiments/methodology of the paper.",
    agent= experiments_methodology_agent,
    context=[leader_task]
)


review_crew = Crew(
    tasks=[leader_task, clarity_agent_tasks, novelty_agent_tasks, experiments_methodology_tasks],
    agents=[novelty_agent,reviewer_leader, experiments_methodology_agent, clarity_agent],
    # manager_llm=ChatOpenAI(temperature=0, model=‘gpt-4o-mini’),
    process=Process.hierarchical,
    memory=True,
    manager_agent=manager,
    # planning=True,
    # planning_llm=ChatOpenAI(model=“gpt-4o”),
)

result = review_crew.kickoff()

print(result)
