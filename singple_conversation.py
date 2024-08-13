import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
os.environ['OPENAI_MODEL_NAME'] = os.getenv('OPENAI_MODEL_NAME')
os.environ['BROWSERBASE_API_KEY'] = 'BROWSERBASE_API_KEY'
os.environ['BROWSERBASE_PROJECT_ID'] = 'BROWSERBASE_PROJECT_ID'

reviewer_system_prompt_path = os.path.abspath("/Users/harry/Desktop/SOS/agent/crew_ai_agent_project/reviewer_system_prompt.txt")

with open(reviewer_system_prompt_path, 'r') as file:
   reviewer_system_prompt = file.read()



paper_path_1 = os.path.abspath("/Users/harry/Desktop/SOS/agent/crew_ai_agent_project/paper_1.txt")
paper_path_2 = os.path.abspath("/Users/harry/Desktop/SOS/agent/crew_ai_agent_project/paper_2.txt")
with open(paper_path_1, 'r') as paper_file_1:
    paper_1 = paper_file_1.read()


with open(paper_path_2, 'r') as paper_file_2:
    paper_2 = paper_file_2.read()


worker_1 = Agent(
    role='worker_1',
    goal="Help review a scientific paper, especially the part assigned to you. Be ready to answer questions from the review_leader and look for answers from the text assigned to you.",
    backstory=f"{reviewer_system_prompt}",
    cache=True,
)


worker_2 = Agent(
    role='worker_2',
    goal="Help review a scientific paper, especially the part assigned to you. Be ready to answer questions from the review_leader and look for answers from the text assigned to you.",
    backstory=f"{reviewer_system_prompt}",
    cache=True,
)


reviewer_leader = Agent(
    role='reviewer_leader',
    goal="To orchestrate and write peer-review style comments for a scientific paper",
    backstory="You are a part of a group that needs to perform ataks that involves a scientific paper. However, the paper is very long, so each agent has only been given a part of it. You are the leader in charge of interacting with the user and coordinating the group to accomplish tasks. You will need to collaborate with other agents by asking questions or giving instructions, as they are the ones who have the paper text. Other agents do not know anything about the task being performed, so it is your responsibility tot convey any information about that task that is necessary for them to provide helpful responses. You may need multiple to do multiple rounds of communications to exchange all the necessary information; you should follow up with other agents if they provide a bad response or seem to have misunderstood the task. In addition, because other agents can only communicate with you but not each other, you may need to help relay information between agents. Because each agent has a adifferent piece of the paper, communication is key for performing tasks that require understanding of the full paper.In addition, depending on the responses you receive, you may need to ask follow-up questions, clarify your requests,or engage in additional discussion to fully reason about the task. To reduece communication errors, after you send a message you should write a short description of what you expect the response to look like. If the reponse you get doesn't match your expectation, you should review it and potentially ask follow-up questions to check if any mistakes or miscommunications have occurred. It could be the case that an agent (including yourself) has misread something or made a logic error.",
    cache=True,
    verbose=True,
)

manager = Agent(
    role='manager',
    goal="To coordinate and manage the workflow of the review process",
    backstory="You are a part of a group that needs to perform ataks that involves a scientific paper. However, the paper is very long, so each agent has only been given a part of it. You are the review manager in charge of control the workflow of the review process. You will coordinate the interaction between the reviewer_leader and worker agents, bridging their communications. ",
    cache=True,
    verbose=True,
)


chunk_1 = Task(
    description=f"Your paper chunk is shown below: --- START OF PAPER --- {paper_1} --- END OF PAPER ---, do not write a review for this task.",
    expected_output="'Ready', if you have understood the assignment",
    agent=worker_1,
)


chunk_2 = Task(
    description=f"Your paper chunk is shown below: --- START OF PAPER --- {paper_2} --- END OF PAPER ---, do not write a review for this task.",
    expected_output="'Ready', if you have understood the assignment",
    agent=worker_2,
)


# broadcast_plan = Task(
#     description="Ask worker_1 to 'provide a summary of the main goals, contributions, and claims from their section of the paper.'",
#     expected_output="A message that asks each agents to provide a summary of the main goals, contributions, and claims from their section of the paper.",
#     agent=reviewer_leader,
# )

leader_task = Task(
    description="Task: Write a list of feedback comments, similar to the suggestions a reviewer might make. In addition, focus on major comments rather than minor comments; major comments are important things that affect the overall impact of the paper, whereas minor comments are small things like grammar check. Be specific in your suggestions, including details about method or resource names and any particular steps the authors should follow. However, don't suggest things that are already included/addressed in the paper. Remember that you can collaborate if necessary. If you want to write comments and/or ask for additional ones, you may want to provide your original comments to that the agent knows what was going on. Your review comments should be specific and express an appropriate level of importance. A comment like 'the authors should add more details about the proposed methods, such as XXX' is bad because it is too generic. Even for a paper with a good method description it is always possible to add more details. ",
    expected_output="A list of feedback comments resembling that of the peer-reviews for scientific papers.",
    agent=reviewer_leader,
)



worker_1_tasks = Task(
    description= "Task: Help the reviewer leader by providing information concerning your section of the paper",
    expected_output="A set of responses to the leaders' requestsd.",
    agent= worker_1,
    context=[chunk_1, leader_task]
)


worker_2_tasks = Task(
    description= "Task: Help the reviewer leader by providing information concerning your section of the paper",
    expected_output="A set of responses to the leaders' requestsd.",
    agent= worker_2,
    context=[chunk_2, leader_task]
)

# )# generate_review_1 = Task(
#     description=f"Review your chunk of the paper and write a summary of it following the instructions. ",
#     expected_output="A review of the first chunk of the paper.",
#     agent= worker_1,
#     context=[chunk_1]
# )

# generate_review_1 = Task(
#     description=f"Review your chunk of the paper and write a summary of it following the instructions. ",
#     expected_output="A review of the first chunk of the paper.",
#     agent= worker_1,
#     context=[chunk_1]
# )


# generate_review_2 = Task(
#     description=f"Review your chunk of the paper and write a summary of it following the instructions.",
#     expected_output="A review of the second chunk of the paper.",
#     agent= worker_2,
#     context=[chunk_2]
# )

# inspect_review_1 = Task(
#     description="Inspect the generated review from worker_1, ask for clarification of technical details/claims from worker_1 if needed.",
#     expected_output="A confirmation if the review needs is very clear, alternatively a request for elaboration on a term or methods.",
#     agent= reviewer_leader,
#     context=[generate_review_1]
# )


# inspect_review_2 = Task(
#     description="Inspect the generated review from worker_2, ask for clarification of technical details/claims from worker_2 if needed.",
#     expected_output="A confirmation if the review needs is very clear, alternatively a request for elaboration on a term or methods.",
#     agent= reviewer_leader,
#     context=[ generate_review_2]
# )


# clarification_1 = Task(
#     description="affirm that the review is clear or provide clarification to reviewer_leader",
#     expected_output="an affirmation or a clarfication.",
#     agent= worker_1,
#     context=[chunk_1,generate_review_1, inspect_review_1]
# )

# clarification_2 = Task(
#     description="affirm that the review is clear or provide clarification to reviewer_leader",
#     expected_output="an affirmation or a clarfication.",
#     agent= worker_2,
#     context=[chunk_2, generate_review_2, inspect_review_2]
# )



# compose_final_review = Task(
#     description="Compose a final review of the paper based on the reviews from worker_1 and worker_2, address the strengths and limitation of the paper, focusing on the core methods and results. Be less generic.",
#     expected_output="A final review the paper.",
#     agent= reviewer_leader,
#     context=[generate_review_1, generate_review_2,]
# )


review_crew = Crew(
    tasks=[chunk_1, chunk_2, leader_task, worker_1_tasks, worker_2_tasks],
    agents=[worker_1, worker_2,reviewer_leader],
    # manager_llm=ChatOpenAI(temperature=0, model='gpt-4o-mini'),
    process=Process.hierarchical,
    memory=True,
    manager_agent=manager,
    # planning=True,
    # planning_llm=ChatOpenAI(model="gpt-4o"),
)



result = review_crew.kickoff()

print(result)
