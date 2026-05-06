import os


MAX_CHARS = 10000


def get_file_content(working_directory, file_path):
    try:
        absolute_working_directory = os.path.abspath(working_directory)
        absolute_target_file = os.path.normpath(os.path.join(absolute_working_directory, file_path))

        if absolute_working_directory != os.path.commonpath([absolute_working_directory, absolute_target_file]):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        
        if not os.path.isfile(absolute_target_file):
            return f'Error: File not found or is not a regular file: "{file_path}"'
        
        ret_content = ''
        with open(absolute_target_file, "r") as f:
            ret_content += f.read(MAX_CHARS)

            if f.read(1):
                ret_content += f'\n\n[...File "{file_path}" truncated at {MAX_CHARS} characters]'

        return ret_content
    except Exception as e:
        raise e
