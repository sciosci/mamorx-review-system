import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process

from model import load_model, list_avail_models
from ai_reviewer.SemanticScholar import SemanticScholar

# from crewai_tools import BrowserbaseLoadTool
paper_path_1 = 'data/paper_section_1.txt'

paper_path_2 = 'data/paper_section_2.txt'

paper_path_3 = 'data/paper_section_3.txt'

paper_path_4 = 'data/paper_section_4.txt'

reviewer_system_prompt_path = 'data/reviewer_system_prompt.txt'

# guideline_path1 = os.path.abspath("/Users/harry/Desktop/SOS/agent/crew_ai_agent_project/experiments_guidelines.txt")
# guideline_path2 = os.path.abspath("/Users/harry/Desktop/SOS/agent/crew_ai_agent_project/limitation_guidelines.txt")
# guideline_path3 = os.path.abspath("/Users/harry/Desktop/SOS/agent/crew_ai_agent_project/clarity_guidelines.txt")

with open(paper_path_1, 'r') as paper_file_1:
    paper_1 = paper_file_1.read()

with open(paper_path_2, 'r') as paper_file_2:
    paper_2 = paper_file_2.read()

with open(paper_path_3, 'r') as paper_file_3:
    paper_3 = paper_file_3.read()

with open(paper_path_4, 'r') as paper_file_4:
    paper_4 = paper_file_4.read()

# with open(guideline_path1, 'r') as file1:
#     experiments_guideline = file1.read()

# with open(guideline_path2, 'r') as file2:
#     limitation_guideline= file2.read()

# with open(guideline_path3, 'r') as file3:
#    clarity_guideline = file3.read()

with open(reviewer_system_prompt_path, 'r') as file:
   reviewer_system_prompt = file.read()


load_dotenv()
# os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
# os.environ['OPENAI_MODEL_NAME'] = os.getenv('OPENAI_MODEL_NAME')
# os.environ['BROWSERBASE_API_KEY'] = 'BROWSERBASE_API_KEY'
# os.environ['BROWSERBASE_PROJECT_ID'] = 'BROWSERBASE_PROJECT_ID'

# web_tool = BrowserbaseLoadTool()


# list_avail_models()
ss_tool = SemanticScholar()
model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
llm = load_model(model_id)

print(" ## Welcome to paper reviewer")

leader_agent = Agent(
    role='Review Leader',
    goal="To coordinate and orchestrate the review for a scientific paper",
    backstory= """
         You are part of a group that needs to perform tasks that involve a scientific paper. However, the paper is very long, so each agent has only been given part of it. You are the leader in charge of interacting with the user and coordinating the group to accomplish tasks. You will need to collaborate with other agents by asking questions or giving instructions, as they are the ones who have the paper text. In some tasks, you will be asked to aggregate the review from all agents and provide feedback to them.
    """,
    llm=llm
)

agent_1 = Agent(
    role='agent_1',
    goal="Help review a scientific paper, especially the part assigned to you. Be ready to answer questions from the leader and look for the answer from the text assigned to you.",
    backstory=f"{reviewer_system_prompt}",
    llm=llm
)

agent_2 = Agent(
    role='agent_2',
    goal="Help review a scientific paper, especially the part assigned to you. Be ready to answer questions from the leader and look for the answer from the text assigned to you.",
    backstory=f"{reviewer_system_prompt}",
    llm=llm
)

agent_3 = Agent(
    role='agent_3',
    goal="Help review a scientific paper, especially the part assigned to you. Be ready to answer questions from the leader and look for the answer from the text assigned to you.",
    backstory=f"{reviewer_system_prompt}",
    llm=llm
)

agent_4 = Agent(
    role='agent_4',
    goal="Help review a scientific paper, especially the part assigned to you. Be ready to answer questions from the leader and look for the answer from the text assigned to you.",
    backstory=f"{reviewer_system_prompt}",
    llm=llm
)

novelty_expert = Agent(
    role='novalty_expert',
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
    tool=[ss_tool]
)

experiment_expert = Agent(
    role='experiment_expert',
    goal="Review the paper for experiments based on the information given by the leader agent, and provide feedback to the leader agent.",
    backstory="""
        You are part of a group of agents that must perform tasks involving a scientific paper. 
        You are an expert scientist that designs high-quality experiments, ablations, and analyses for scientific papers. 
        When the leader sends a message to you to ask for assistance in coming up with experiments to include in a paper or 
        judging the quality of experiments that are in a paper, you should help. 
        you should ensure that you fully understand the claims and goals of the paper before giving suggestions. 
        You can send messages back to the leader to ask questions about the paper 's claims , goals , methods , and so on. 
        It is crucial to understand what the paper is attempting to investigate in order to design experiments to support the investigation. 
        Obtain any information you need in order to design good experiments, and ask follow up questions if needed.
        Be detailed and specific in the experimental suggestions you give. What should the setup be? What settings or methods should be compared? 
        What metrics or measurement techniques should be used? How should the results be analyzed? Make it clear which specific details are important 
        and why (e.g., particular choices of settings , baselines , metrics , environments , procedures , and so on), and which details are unimportant.
        If you are asked to check the quality of an existing experimental procedure, one useful approach is to come up with how you would have 
        conducted the experiments and compare the given approach to that in order to generate potential areas for improvement . 
        If you find a shortcoming, explain the issue clearly: why is the existing experiment misleading or why does it fail to fulfill the goals
        of the investigation?
        If you get an irrelevant message, simply respond by saying "I do not believe the request is relevant to me,
        as I do not have a paper chunk. I will stand by for further instructions."
    """,
    llm=llm,
    verbose=True
)

clarity_expert = Agent(
    role='clarity_expert',
    goal="Review the paper with respect to clarity and reproducibility based on the information given by the leader agent, and provide feedback to the leader agent.",
    backstory="""
        You are part of a group of agents working with a scientific paper. 
        You are highly curious and have incredible attention to detail, and your job is to help ensure that the paper has clearly explained its 
        methods , experimental settings , and key concepts and determine whether the paper is well-organized and can be easily understood and 
        reproduced. The group leader will give you a summary of the paper, and you should ask questions to fully understand the paper 's methods, 
        experimental settings, concepts. This includes asking follow -up questions as needed. Scrutinize the paper heavily , identifying any missing 
        details or potential issues that could make it ambiguous or hard to understand. Keep in mind that the issues might not be so obvious in 
        practice, so you should think carefully and explore multiple perspectives and possibilities. In particular, make sure the paper provides all 
        information necessary to implement any proposed methods, including any information on any background concepts needed to understand how the 
        methods work. Also ensure that the paper provides enough information to replicate the experimental hyperparameters, specifications, or other 
        implementation details. 
        Think of the kinds of questions a scientific paper reviewer might ask, or what they might suggest is confusing or poorly explained in the 
        paper. Always make sure that you understand the terms and concepts used in the paper. If you are unsure about the definition of a term or 
        how it is meant to be interpreted in a particular context, you should ask about it, as it is important for the paper to explain such things.
        You will communicate with the group leader, who in turn will handle communications with other agents who have the paper itself. Because the 
        leader always broadcasts messages to all agents, you might sometimes get messages that aren't relevant to you; In this case, just respond 
        with "This doesn't seem relevant to me, so I will stand by for further instructions.". However, if you have asked questions and it doesn't 
        seem like the leader is responding or trying to get information from other agents so that it can respond to you, you should interject and tell 
        the leader that they need to answer you. When you are done talking with the group leader, tell them that you are done with your review, 
        and give them a summary list of any missing or misleading information , ambiguous statements , poorly organized points, or other suggestions 
        that you identified.
        """,
    llm=llm,
    verbose=True
)

# Each agent is provided with their specific chunk of the paper directly in their initial task.
chunk_1 = Task(
    description=f"Your paper chunk is shown below: --- START OF PAPER --- {paper_1} --- END OF PAPER ---, do not write a review for this task.",
    expected_output="'Ready', if you have understood the assignment",
    agent=agent_1,
)

chunk_2 = Task(
    description=f"Your paper chunk is shown below: --- START OF PAPER --- {paper_2} --- END OF PAPER ---, do not write a review for this task.",
    expected_output="'Ready', if you have understood the assignment",
    agent=agent_2,
)

chunk_3 = Task(
    description=f"Your paper chunk is shown below: --- START OF PAPER --- {paper_3} --- END OF PAPER ---, do not write a review for this task.",
    expected_output="'Ready', if you have understood the assignment",
    agent=agent_3,
)

chunk_4 = Task(
    description=f"Your paper chunk is shown below: --- START OF PAPER --- {paper_4} --- END OF PAPER ---, do not write a review for this task.",
    expected_output="'Ready', if you have understood the assignment",
    agent=agent_4,
)

broadcast_plan = Task(
    description="Ask all of agent_1, agent_2, agent_3 and agent_4 to 'provide a summary of the main goals, contributions, and claims from their section of the paper.'",
    expected_output="A message that asks each agents to provide a summary of the main goals, contributions, and claims from their section of the paper.",
    agent=leader_agent,
)

# Task flow directly ties each agent to their respective chunk.
generate_review_1 = Task(
    description="Review your chunk of the paper following the instructions from the leader_agent.",
    expected_output="A review of the first part of the paper.",
    agent=agent_1,
    context=[chunk_1, broadcast_plan]
)

generate_review_2 = Task(
    description="Review your chunk of the paper following the instructions from the leader_agent.",
    expected_output="A review of the second part of the paper.",
    agent=agent_2,
    context=[chunk_2, broadcast_plan]
)

generate_review_3 = Task(
    description="Review your chunk of the paper following the instructions from the leader_agent.",
    expected_output="A review of the third part of the paper.",
    agent=agent_3,
    context=[chunk_3, broadcast_plan]
)

generate_review_4 = Task(
    description="Review your chunk of the paper following the instructions from the leader_agent.",
    expected_output="A review of the fourth part of the paper.",
    agent=agent_4,
    context=[chunk_4, broadcast_plan]
)

Feedback_to_agent_1 = Task(
    description="Comment on the review of agent_1, ask for clarification about details in agent_1's section of the paper if needed. Otherwise, confirm that agent_1 has completed the task. Avoid entering a loop by asking for the same information multiple times.",
    expected_output="A message to agent_1.",
    agent=leader_agent,
    context=[generate_review_1]
    ,)

agent_1_reponse_to_leader = Task(
    description="Respond to the feedback from the leader_agent and provide clarifications if needed, otherwise confirm that you have completed the task. Avoid reduplicate what you have done in the generate_review step.",
    expected_output="A response to the leader_agent.",
    agent=agent_1,
    context=[Feedback_to_agent_1]
)

Feedback_to_agent_2 = Task(
    description="Comment on the review of agent_2, ask for clarification about details in agent_1's section of the paper if needed. Otherwise, confirm that agent_1 has completed the task. Avoid entering a loop by asking for the same information multiple times.",
    expected_output="A message to agent_2.",
    agent=leader_agent,
    context=[generate_review_2]
    ,)

agent_2_reponse_to_leader = Task(
    description="Respond to the feedback from the leader_agent and provide clarifications if needed, otherwise confirm that you have completed the task. Avoid reduplicate what you have done in the generate_review step.",
    expected_output="A response to the leader_agent.",
    agent=agent_2,
    context=[Feedback_to_agent_2]
)

Feedback_to_agent_3 = Task(
    description="Comment on the review of agent_3, ask for clarification about details in agent_1's section of the paper if needed. Otherwise, confirm that agent_1 has completed the task. Avoid entering a loop by asking for the same information multiple times.",
    expected_output="A message to agent_3.",
    agent=leader_agent,
    context=[generate_review_3]
    ,)

agent_3_reponse_to_leader = Task(
    description="Respond to the feedback from the leader_agent and provide clarifications if needed, otherwise confirm that you have completed the task. Avoid reduplicate what you have done in the generate_review step.",
    expected_output="A response to the leader_agent.",
    agent=agent_3,
    context=[Feedback_to_agent_3]
)


Feedback_to_agent_4 = Task(
    description="Comment on the review of agent_4, ask for clarification about details in agent_1's section of the paper if needed. Otherwise, confirm that agent_1 has completed the task. Avoid entering a loop by asking for the same information multiple times.",
    expected_output="A message to agent_4.",
    agent=leader_agent,
    context=[generate_review_4]
    ,)

agent_4_reponse_to_leader = Task(
    description="Respond to the feedback from the leader_agent and provide clarifications if needed, otherwise confirm that you have completed the task. Avoid reduplicate what you have done in the generate_review step.",
    expected_output="A response to the leader_agent.",
    agent=agent_4,
    context=[Feedback_to_agent_4]
)


compile_summarize = Task(
    description="Compile the reviews from all agents into a single piece, avoiding entering a loop by asking the agents to repeat the same process in broadcast_plan and Feedback to agents.",
    expected_output="A compiled review combining all reviews and responses from agent_1, agent_2, agent_3, and agent_4.",
    agent=leader_agent,
    context=[generate_review_1, generate_review_2, generate_review_3, generate_review_4, agent_1_reponse_to_leader, agent_2_reponse_to_leader, agent_3_reponse_to_leader, agent_4_reponse_to_leader]
)

expert_examination_1 = Task(
    description="Review the compiled summary by leader_agent and provide feedback on the experiments.",
    expected_output="Feedback on the experiments in the paper.",
    agent=expert_agent,
    context=[compile_summarize]
)

leader_review_responses = Task(
    description="Review the feedback from the expert and seek clarifications from agents if needed.",
    expected_output="Responses to the expert feedback concerning the sections of the paper.",
    agent=leader_agent,
    context=[compile_summarize, expert_examination_1]
)

revise_review = Task(
    description="Revise your review based on the feedback from the expert and the responses from agent_1, agent_2, agent_3, and agent_4.",
    expected_output="A revised review.",
    agent=leader_agent,
    context=[compile_summarize, expert_examination_1, leader_review_responses]
)

crew = Crew(
    agents=[agent_1, agent_2, agent_3, agent_4, leader_agent, expert_agent],
    tasks=[
        chunk_1, chunk_2, chunk_3, chunk_4,
        broadcast_plan,
        generate_review_1, generate_review_2, generate_review_3, generate_review_4,
        Feedback_to_agent_1, agent_1_reponse_to_leader,
        Feedback_to_agent_2, agent_2_reponse_to_leader,
        Feedback_to_agent_3, agent_3_reponse_to_leader,
        Feedback_to_agent_4, agent_4_reponse_to_leader,
        compile_summarize,
        expert_examination_1,
        leader_review_responses,
        revise_review
    ],
    process=Process.sequential,
    verbose=True,
    memory=True
)

result = crew.kickoff()

print(result)
