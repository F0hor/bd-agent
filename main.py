import os
import argparse
from dotenv import load_dotenv
from google import genai

from functions.call_funcs import available_functions


system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""


parser = argparse.ArgumentParser(description="Chatbot")
parser.add_argument("user_prompt", type=str, help="User prompt")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()


load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if api_key == None or api_key == "":
    raise Exception('No API key')

client = genai.Client(api_key=api_key)


messages = [genai.types.Content(role="user", parts=[genai.types.Part(text=args.user_prompt)])]

response = client.models.generate_content(
    model='gemini-2.5-flash', 
    contents=messages,
    config=genai.types.GenerateContentConfig(
        tools=[available_functions], system_instruction=system_prompt#, temperature=0
        ),
    )

if response.usage_metadata.candidates_token_count == None:
    raise Exception("No response metadata")

if args.verbose == True:
    print(f"User prompt: {args.user_prompt}")
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

if response.function_calls != None:
    for call in response.function_calls:
        print(f"Calling function: {call.name}({call.args})")
else:
    print(response.text)
