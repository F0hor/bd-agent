import os


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
