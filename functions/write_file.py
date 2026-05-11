import os
from google import genai


def write_file(working_directory, file_path, content):
    try:
        absolute_working_directory = os.path.abspath(working_directory)
        absolute_target_file = os.path.normpath(os.path.join(absolute_working_directory, file_path))

        #print(absolute_working_directory)
        #print(absolute_target_file)

        if absolute_working_directory != os.path.commonpath([absolute_working_directory, absolute_target_file]):
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        
        if os.path.isdir(absolute_target_file):
            return f'Error: Cannot write to "{file_path}" as it is a directory'
        
        os.makedirs(os.path.split(absolute_target_file)[0], exist_ok=True)
        
        with open(absolute_target_file, "w") as f:
            f.write(content)

        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        raise e
    
schema_write_file = genai.types.FunctionDeclaration(
    name="write_file",
    description="Overwrites the file at given file path (relative to the working directory), with given content",
    parameters=genai.types.Schema(
        type=genai.types.Type.OBJECT,
        required=['file_path'],
        properties={
            "file_path": genai.types.Schema(
                type=genai.types.Type.STRING,
                description="File path to be overwritten, relative to the working directory",
            ),
            "content": genai.types.Schema(
                type=genai.types.Type.STRING,
                description="Content to be written to file at file path"
            )
        },
    ),
)
