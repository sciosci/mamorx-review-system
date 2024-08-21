from MultiAgentWorkflow import MultiAgentWorkflow

""" This would be the main function that initiate the PDF parsing processing and feed the data to the functions. This is just
    a skeleton of the function. Ideally the system should feed the text, titles, and other information as parameters for the 
    4 systems.
"""


def main():
    # Instantiate the MultiAgentWorkflow
    workflow = MultiAgentWorkflow(
        base_dir='/Users/harry/Desktop/SOS/agent/crew_ai_agent_project',
        model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
        prompts_file='/Users/harry/Desktop/SOS/agent/crew_ai_agent_project/prompts.json'
    )

    # Initiate the workflow
    workflow.initiate_workflow()

if __name__ == "__main__":
    main()
