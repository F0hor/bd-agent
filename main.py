import os
import argparse
from dotenv import load_dotenv
from google import genai

from functions.call_funcs import available_functions, call_function


MAX_AGENT_ITER = 20


system_prompt = """
You are an expert coding agent designed to help users solve programming problems, 
write code, and manage file operations. You have access to file system tools and 
Python execution capabilities. Your goal is to efficiently understand user requests, 
implement solutions, and provide clear explanations of your work.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

1. get_files_info
- Purpose: List files and directories in a specified path along with thier size
- Parameters: path (string) - directory to list
- Returns: String where on each line is file/directory name with metadata
- Use when: You need to explore the project structure or find specific files

2. get_file_content
- Purpose: Read the contents of a file
- Parameters: file_path (string) - path to the file
- Returns: File contents as text
- Use when: You need to understand existing code, view file structure, or debug

3. run_python_file
- Purpose: Execute Python files with optional command-line arguments
- Parameters: file_path (string), args (optional array of strings)
- Returns: stdout, stderr, and exit code
- Use when: You need to run code, test implementations, or validate solutions

4. write_file
- Purpose: Completely replace a file's contents
- Parameters: file_path (string), content (string)
- Returns: Success confirmation or error
- Use when: Creating new files or modifying existing ones
- Warning: This irreversibly replaces file contents

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.

Operating Principles:

1. **Exploration First**: Before modifying files, use ListFiles and ReadFile to 
   understand the existing structure and context.

2. **Incremental Testing**: After writing code, use ExecutePython to test it 
   immediately and verify correctness before moving forward.

3. **Clear Communication**: Explain what you're doing at each step. Narrate your 
   exploration and reasoning so the user understands your approach.

4. **Error Handling**: When code fails, read error messages carefully, debug 
   systematically, and iterate on solutions.

5. **Preserve Existing Work**: Only use OverwriteFile when necessary. Ask for 
   confirmation if modifying critical files, or offer to create backups.

6. **Path Management**: Always use relative or absolute paths consistently. 
   Clarify the working directory if ambiguous.

7. **Code Quality**: Write clean, well-commented Python code. Follow PEP 8 
   conventions when possible.
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

for _ in range(MAX_AGENT_ITER):
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

    if response.candidates != None and response.candidates != []:
        for cand in response.candidates:
            messages.append(cand)

    if response.function_calls != None:
        result_parts = []
        for call in response.function_calls:
            result = call_function(call, args.verbose)
            if result.parts == None or result.parts == []:
                raise Exception(f"Function ({call.name}) call result returned with None or empty parts list")
            
            result_response = result.parts[0].function_response
            if result_response == None:
                raise Exception("Function call response object is None")
            if result_response.response == None or result_response.response == dict():
                raise Exception("Response atribute of function call response object is None or empty")
            
            result_parts.append(result.parts[0])
            if args.verbose:
                print(f"-> {result.parts[0].function_response.response}")

        messages.append(genai.types.Content(role="user", parts=result_parts))
    else:
        print('Final response:')
        print(response.text)
        exit(0)

print("The agent has reached maximal number of iterations allowed without a text response, this may indicate that the agent was not able to finish its task")
exit(1)
