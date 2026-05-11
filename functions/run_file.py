import os
import subprocess
from google import genai


def run_python_file(working_directory, file_path, args=None):
    try:
        absolute_working_directory = os.path.abspath(working_directory)
        absolute_target_file = os.path.normpath(os.path.join(absolute_working_directory, file_path))

        if absolute_working_directory != os.path.commonpath([absolute_working_directory, absolute_target_file]):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        
        if not os.path.isfile(absolute_target_file):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        
        if absolute_target_file[-3:] != '.py':
            return f'Error: "{file_path}" is not a Python file'
        
        command = ["python", absolute_target_file]

        if args != None:
            command.extend(args)

        completed_process = subprocess.run(
            command,
            text=True,
            capture_output=True,
            timeout=30
            )
        
        ret_str = ''

        if completed_process.returncode != 0:
            ret_str += f'Process exited with code {completed_process.returncode}\n'
        if completed_process.stdout == '' and completed_process.stderr == '':
            ret_str += 'No output produced\n'
        else:
            ret_str += f'STDOUT: {completed_process.stdout}\nSTDERR: {completed_process.stderr}'

        return ret_str
    except Exception as e:
        raise e
    
schema_run_python_file = genai.types.FunctionDeclaration(
    name="run_python_file",
    description="Returns the exit code along with contents of STDOUT and STDERR (if both STDOUT and STDERR are empty returns 'No output produced' instead)",
    parameters=genai.types.Schema(
        type=genai.types.Type.OBJECT,
        required=['file_path'],
        properties={
            "file_path": genai.types.Schema(
                type=genai.types.Type.STRING,
                description="File path to python file to be executed, relative to the working directory",
            ),
            "args": genai.types.Schema(
                type=genai.types.Type.ARRAY,
                items=genai.types.Schema(
                    type=genai.types.Type.STRING
                ),
                description="List of arguments to be passed to the executed file"
            )
        },
    ),
)
