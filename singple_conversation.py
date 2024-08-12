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
    goal="Help review a scientific paper, especially the part assigned to you. Be ready to answer questions from the review_leader and look for the answer from the text assigned to you.",
    backstory=f"{reviewer_system_prompt}",
    cache=True,
)


worker_2 = Agent(
    role='worker_2',
    goal="Help review a scientific paper, especially the part assigned to you. Be ready to answer questions from the review_leader and look for the answer from the text assigned to you.",
    backstory=f"{reviewer_system_prompt}",
    cache=True,
)




reviewer_leader = Agent(
    role='reviewer_leader',
    goal="To coordinate and orchestrate the review for a scientific paper",
    backstory="You are part of a group that needs to perform tasks that involve a scientific paper.However, the paper is very long, so each 'worker' agents has only been given part of it, your task is to manage the whole review workflow: You need to recieve summaries from each worker and orchestrate it into a unified revirew. You can ask for clarifications and explanations from the workers about the section of the paper they have access to, but you should never require the full text of any sections of the paper. You should only begin writing the final review once you have summaries from all workers. ",
    cache=True,
    verbose=False,
)


# chunk_1 = Task(
#     description=f"Your paper chunk is shown below: --- START OF PAPER --- {paper_1} --- END OF PAPER ---, do not write a review for this task.",
#     expected_output="'Ready', if you have understood the assignment",
#     agent=worker_1,
# )


# chunk_2 = Task(
#     description=f"Your paper chunk is shown below: --- START OF PAPER --- {paper_2} --- END OF PAPER ---, do not write a review for this task.",
#     expected_output="'Ready', if you have understood the assignment",
#     agent=worker_2,
# )


# broadcast_plan = Task(
#     description="Ask worker_1 to 'provide a summary of the main goals, contributions, and claims from their section of the paper.'",
#     expected_output="A message that asks each agents to provide a summary of the main goals, contributions, and claims from their section of the paper.",
#     agent=reviewer_leader,
# )

generate_review_1 = Task(
    description=f"Review your chunk of the paper and write a summary of it following the instructions from the review_leader. Your paper chunk is shown below: --- START OF PAPER --- {paper_1} --- END OF PAPER ---",
    expected_output="A review of the first chunk of the paper.",
    agent= worker_1,
    # context=[chunk_1]
)


generate_review_2 = Task(
    description=f"Review your chunk of the paper and write a summary of it following the instructions from the review_leader.Your paper chunk is shown below: --- START OF PAPER --- {paper_2} --- END OF PAPER ---",
    expected_output="A review of the second chunk of the paper.",
    agent= worker_2,
    # context=[chunk_2]
)

compose_final_review = Task(
    description="Compose a final review of the paper based on the reviews from worker_1 and worker_2",
    expected_output="A final review the paper.",
    agent= reviewer_leader,
    context=[generate_review_1, generate_review_2]
)


review_crew = Crew(
    tasks=[generate_review_1, generate_review_2, compose_final_review],
    agents=[worker_1, worker_2],
    # manager_llm=ChatOpenAI(temperature=0, model='gpt-4o'),
    process=Process.hierarchical,
    memory=True,
    manager_agent=reviewer_leader,
    planning=True,
    planning_llm=ChatOpenAI(model="gpt-4o"),
)



result = review_crew.kickoff()

print(result)
