import os


def get_files_info(working_directory, directory="."):
    try:
        absolute_working_directory = os.path.abspath(working_directory)
        absolute_target_directory = os.path.normpath(os.path.join(absolute_working_directory, directory))

        if not absolute_working_directory == os.path.commonpath([absolute_working_directory, absolute_target_directory]):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        
        if not os.path.isdir(absolute_target_directory):
            return f'Error: "{directory}" is not a directory'
        
        dir_contents = os.listdir(absolute_target_directory)
        ret_str = ''
        for name in dir_contents:
            target_content = os.path.join(absolute_target_directory, name)
            ret_str += f"- {name}: file_size={os.path.getsize(target_content)} bytes, is_dir={os.path.isdir(target_content)}\n"

        return ret_str
    except Exception as e:
        raise e
