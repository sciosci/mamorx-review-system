from litellm import completion
import litellm 


response = completion(
    model="ollama/llama3.1", 
    messages=[{ "content": "respond in 20 words. who are you?","role": "user"}], 
    api_base="http://localhost:11434"
)
print(response)