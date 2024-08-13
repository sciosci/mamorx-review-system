import boto3
from dotenv import load_dotenv
from langchain_aws import ChatBedrock

def list_avail_models():
    # Initialize the Bedrock client
    load_dotenv()
    client = boto3.client('bedrock', region_name='us-east-1')

    # List available foundation models
    response = client.list_foundation_models()
    # Check and iterate over the 'modelSummaries' key
    if 'modelSummaries' in response:
        for model in response['modelSummaries']:
            print(f"Model ID: {model['modelId']}")
            print(f"Model Name: {model['modelName']}")
            print(f"Provider: {model['providerName']}")
            print(f"Input Modalities: {model['inputModalities']}")
            print(f"Output Modalities: {model['outputModalities']}")
            print(f"Inference Types Supported: {model['inferenceTypesSupported']}")
            print(f"Model Lifecycle Status: {model['modelLifecycle']['status']}")
            print("-" * 40)
    else:
        print("No models found or an error occurred.")

def load_model(model_id:str):
    load_dotenv()
    llm = ChatBedrock(
        model_id = model_id
        )
    return llm