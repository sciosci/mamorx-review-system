import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
# from crewai_tools import BrowserbaseLoadTool
paper_path_1 = os.path.abspath("/Users/harry/Desktop/SOS/agent/crew_ai_agent_project/paper_1.txt")

paper_path_2 = os.path.abspath("/Users/harry/Desktop/SOS/agent/crew_ai_agent_project/paper_2.txt")

paper_path_3 = os.path.abspath("/Users/harry/Desktop/SOS/agent/crew_ai_agent_project/paper_3.txt")

paper_path_4 = os.path.abspath("/Users/harry/Desktop/SOS/agent/crew_ai_agent_project/paper_4.txt")

guideline_path1 = os.path.abspath("/Users/harry/Desktop/SOS/agent/crew_ai_agent_project/experiments_guidelines.txt")
guideline_path2 = os.path.abspath("/Users/harry/Desktop/SOS/agent/crew_ai_agent_project/limitation_guidelines.txt")
guideline_path3 = os.path.abspath("/Users/harry/Desktop/SOS/agent/crew_ai_agent_project/clarity_guidelines.txt")

with open(paper_path_1, 'r') as paper_file_1:
    paper_1 = paper_file_1.read()

with open(paper_path_2, 'r') as paper_file_2:
    paper_2 = paper_file_2.read()

with open(paper_path_3, 'r') as paper_file_3:
    paper_3 = paper_file_3.read()

with open(paper_path_4, 'r') as paper_file_4:
    paper_4 = paper_file_4.read()

with open(guideline_path1, 'r') as file1:
    experiments_guideline = file1.read()

with open(guideline_path2, 'r') as file2:
    limitation_guideline= file2.read()

with open(guideline_path3, 'r') as file3:
   clarity_guideline = file3.read()


load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
os.environ['OPENAI_MODEL_NAME'] = os.getenv('OPENAI_MODEL_NAME')
os.environ['BROWSERBASE_API_KEY'] = 'BROWSERBASE_API_KEY'
os.environ['BROWSERBASE_PROJECT_ID'] = 'BROWSERBASE_PROJECT_ID'

# web_tool = BrowserbaseLoadTool()

print(" ## Welcome to paper reviewer")

# leader_agent = Agent(
#     role='Review Leader',
#     goal=f"Given a first part of the .",
#     backstory= """
#         you are a review chair for an academic journals. You have been assigned to lead a review process for a paper that has been submitted to a conference. However, your job is not to actually review the paper yourself, but to give the paper to each of the reviewer type and inform them their tasks
#     """,
#     # tools= [{"name":"web_tool", "instance": web_tool}],
# )

summarizer_agent_1 = Agent(
    role='summarizer_1',
    goal="given the first part of the article, summarize it in a few sentences. Leave minor details out and focus on the main points, to avoid loss of information, technical details should be maximally preserved.",
    backstory= """
        you are a excellent summarizer, you have been assigned to summarize the part of paper given to you, avoid loss of information, technical details should be maximally preserved.
    """,
)

summarizer_agent_2 = Agent(
    role='summarizer_2',
    goal="given a part of the article, summarize it in a few sentences. Leave minor details out and focus on the main points, to avoid loss of information, technical details should be maximally preserved. If you are passed the with the summarize of the previous part of the paper, you should preserve it and add on top of it with the summary of the part assigned to you.",
    backstory= """
        you are a excellent summarizer, you have been assigned to summarize the part of paper given to you, avoid loss of information, technical details should be maximally preserved.
    """,
)

summarizer_agent_3 = Agent(
    role='summarizer_3',
    goal="given a part of the article, summarize it in a few sentences. Leave minor details out and focus on the main points, to avoid loss of information, technical details should be maximally preserved. If you are passed the with the summarize of the previous part of the paper, you should preserve it and add on top of it with the summary of the part assigned to you",
    backstory= """
        you are a excellent summarizer, you have been assigned to summarize the part of paper given to you, avoid loss of information, technical details should be maximally preserved.
    """,
)

summarizer_agent_4= Agent(
    role='summarizer_4',
    goal="given a part of the article, summarize it in a few sentences. Leave minor details out and focus on the main points, to avoid loss of information, technical details should be maximally preserved. If you are passed the with the summarize of the previous part of the paper, you should preserve it and add on top of it with the summary of the part assigned to you",
    backstory= """
        you are a excellent summarizer, you have been assigned to summarize the part of paper given to you, avoid loss of information, technical details should be maximally preserved.
    """,
)


clarity_agent = Agent(
    role='clarity reviewer',
    goal='Given an academic paper for review and a guideline from the leader, your role is to review the paper for clarity and provide feedback to the author.',
    backstory= """ 
        you are a senior researcher in a university and an expert in academic writing. You have been assigned to peer-review a paper that has been submitted to a conference.
    """,
    verbose=True
    )

limitation_agent = Agent(
    role='limitation reviewer',
    goal='Given an academic paper for review and a guideline from the leader, your role is to access the limitation of the paper. The guidelines concerning the authors limitation is provided by the leader',
    backstory= """ 
        you are a senior researcher in a university and an expert in academic writing. You have been assigned to peer-review a paper that has been submitted to a conference.
    """,
    verbose=True
    )

experiment_agent = Agent(
    role='experiment reviewer',
    goal='Given an academic paper for review and a guideline from the leader, your role is to assess the experiment part of the paper. The guidelines concerning the authors limitation is provided by the leader. Please be conise',
    backstory= """ 
        you are a senior researcher in a university and an expert in experiments design. You have been assigned to peer-review a paper that has been submitted to a conference.
    """,
    verbose=True
    )

composer_agent = Agent(
    role='composer reviewer',
    goal='Your role is to take in each reviewer agents review and compose a final review that will be sent to the author of the paper. You need to make sure that the final review is coherent and well structured. The review should only address top level issues and not go into the details of each review.',
    backstory= """ 
        you are a meta-review reviewer for the jorunals, you are good at composing a final reivew after consulting the advices on the experts.
    """,
    )


# task1 = Task(
#     description=f'Initiate the review process by prompting the reviewer agents the full text of the paper: {paper}, that they will be reviewing as well as the journals guildlines for each reviewer according to their roles. This task requires the the reviewers guidelines here {guideline}',
#     expected_output='Prompt the reviewer agents the full text of the paper that they will be reviewing.',
#     agent = leader_agent
# )


summarize_1 = Task(
    description=f"Summarize the first part of the paper {paper_1} ,",
    expected_output='Summarize the first part of the paper',
    agent=summarizer_agent_1,
    output_file ='summary_1.txt',
)


summarize_2 = Task(
    description=f'Summarize the second part of the paper {paper_2}, you should keep the summary of the previous part and make them coherent.',
    expected_output='Summarize the first part of the paper',
    agent=summarizer_agent_2,
    context= [summarize_1],
    output_file ='summary_2.txt',
)

summarize_3 = Task(
    description=f'Summarize the third part of the paper {paper_3} , you should keep the summary of the previous part and make them coherent.',
    expected_output='Summarize the third part of the paper',
    agent=summarizer_agent_3,
    context= [summarize_2],
    output_file ='summary_3.txt',
)


summarize_4 = Task(
    description=f'Summarize the fourth part of the paper {paper_4}, you should keep the summary of the previous part.',
    expected_output='Summarize the fourth part of the paper',
    agent=summarizer_agent_4,
    context= [summarize_3],
    output_file ='finall_summary.txt',
)



task2 = Task(
    description= f'Given the summary of an academic paper , review it and write an review with an focused on the clarity of the paper, whether it is clearly written and easy to follow and whether the author s arguments are well supported. The detailed guidline is {clarity_guideline}.',
    expected_output='write an part of a peer-review that discuss the clarity of the paper, given the guidlines provided by the leader agent. Please be very concise and you can ignore minor issues like grammar and spelling. maximally 200 words',
    agent=clarity_agent,
    output_file ='clarity_review.txt',
    context= [summarize_4]
)


task3= Task(
    description= f'Given an summary of academic paper, review it and write an review with an focused on the limitation of the paper, the detailed guidline is provided by the leader agent. The detailed guidline is {limitation_guideline}.',
    expected_output='write an part of a peer-review that discuss the limitation of the paper, given the guidlines provided by the leader agent. Please be very concise and you can ignore minor issues like grammar and spelling. maximally 200 words',
    agent= limitation_agent,
    output_file ='limitation_review.txt',
    context= [summarize_4]
)

task4= Task(
    description= f'Given an summary of an academic paper:, review it and write an review with an focused on the experiments of the paper, the detailed guidline is provided by the leader agent. The detailed guidline is {experiments_guideline}.',
    expected_output='write an part of a peer-review that discuss the experiments of the paper, given the guidlines provided by the leader agent.Please be very concise and you can ignore minor issues like grammar and spelling. maximally 200 words',
    agent= experiment_agent,
    output_file ='experiments_review.txt',
    context= [summarize_4]
)

task5 = Task(
    description= 'Given many parts reviews produced by task2, task3, and task4, construct a concise and coherent final review that will be sent to the author of the paper. The final review should only address top level issues and not go into the details of each review.',
    expected_output='write an concise version of a final review that will be sent to the author of the paper.',
    agent= composer_agent,
    output_file ='final_review.txt',
    context= [task2, task3, task4]
)


crew = Crew(
    agents=[summarizer_agent_1,summarizer_agent_2,summarizer_agent_3, summarizer_agent_4, clarity_agent, limitation_agent, experiment_agent, composer_agent],
    tasks=[summarize_1, summarize_2, summarize_3, summarize_4, task2, task3, task4, task5],
    process=Process.sequential,
    verbose=True,
    memory=True
)

result = crew.kickoff()

print(result)