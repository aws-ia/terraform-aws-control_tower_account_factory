import subprocess
import inspect
import pprint
import os
import re
from typing import List
import json
import sys

def red(text):
    return f"\033[1;91m{text}\033[0m"

def cyan(text):
    return f"\033[1;96m{text}\033[0m"

def yellow(text):
    return f"\033[1;93m{text}\033[0m"

def load_json(file_path):
    if not os.path.exists(file_path):
        sys.exit(red('ERROR: File does not exist: ' + file_path))
    with open(file_path, encoding='UTF-8') as file:
        return json.load(file)
    return None

def increment_tag_version(tags: List[str]):
    if tags:
        latest_semantic_version_parts = [0, 0, 0]
        semantic_version_separator = '.'

        for tag in tags:
            semver_regex = '^v\d*\.\d*\.\d*$'
            is_valid_semver = re.match(semver_regex, tag)

            if is_valid_semver:
                formatted_version = re.sub('[^0-9.]', '', tag)
                version_parts = formatted_version.split(sep=semantic_version_separator)
                version_parts_ints = map(
                    lambda version: int(version),
                    version_parts
                )

                iterated_major_version, iterated_minor_version, iterated_patch_version = version_parts_ints
                latest_major_version, latest_minor_version, latest_patch_version = latest_semantic_version_parts

                if iterated_major_version > latest_major_version \
                        or (
                        iterated_major_version == latest_major_version
                        and iterated_minor_version > latest_minor_version) \
                        or (
                        iterated_major_version == latest_major_version
                        and iterated_minor_version == latest_minor_version
                        and iterated_patch_version > latest_patch_version):
                    latest_semantic_version_parts = [
                        iterated_major_version,
                        iterated_minor_version,
                        iterated_patch_version
                    ]

        patch_version_index = 2
        incremented_patch_version = latest_semantic_version_parts[patch_version_index] + 1
        latest_semantic_version_parts[patch_version_index] = incremented_patch_version

        return f'v{".".join(map(str, latest_semantic_version_parts))}'
    else:
        return 'v0.0.1'

def print_api_call_info(msg: str, type: str, url: str, payload: str, response: str):
    if len(msg) > 0:
        print(msg)
    print(f"  {type} to {url}")
    print("  payload:")
    print("    "+pprint.pformat(payload).replace("'",'"').replace('False','"False"').replace('True','"True"').replace("\n","\n    "))
    print("  response:")
    print("    "+pprint.pformat(response,).replace("'",'"').replace("\n","\n    "))

def obscure_env_var_secret(env_var_secret: str):
    val=os.environ.get(env_var_secret)
    if val == None or len(val) == 0:
        return ""
    # don't show any of the secret if it is short
    if len(val) < 3:
        return "*"*(len(val))
    show=4 # only show last 4 chars of the secret
    if len(val) * 0.3 < show:
        # show less than 4 chars if secret is short
        show=int(len(val) * 0.3)
        if show == 0:
            show = 1
    return f"{'*'*(len(val)-show)}{val[-show:]}"

def print_struct(data: str, indent: str = ""):
    print(f"{indent}"+pprint.pformat(data).replace("'",'"').replace("\n",f"\n{indent}"))

def print_ssm_parameter_to_write(name:str,
                                account_id:str,
                                current_region:str,
                                value:str,
                                indent:str):
    print(f"{indent}Setting SSM Parameter '/tlz/{name}'")
    print(f"{indent}  in account '{account_id}'")
    print(f"{indent}  in region '{current_region}''")
    print(f"{indent}  to value:")
    print(f"{indent}    "+pprint.pformat(value).replace("\n",f"\n{indent}"))

class SubProcessRunError(Exception):
    pass

# Execute "cmd" in a subprocess
# - Return an array of the output of the command, and the return code
# - Don't include "cmd" in the returned output if no_echo==True
# - The output returned will be indented by the same amount that the passed
#   'cmd' is indented by (i.e. number of leading spaces in 'cmd'), plus 2 additional
#   spaces (so that the output is clearly associated with the 'cmd' that was executed)
def _subprocess_call(cmd:str, no_echo:bool = False):
    result=""
    if cmd == None or len(cmd) == 0:
        return [ 0, "" ]
    indent_level = re.search(r'\S',cmd).start()
    indent=" "*indent_level
    cmd = cmd.lstrip()
    if not ( no_echo ):
        result=f"{result}\n{indent}{cmd}"
    process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    stdout=process.stdout.rstrip().lstrip()
    stderr=process.stderr.rstrip().lstrip()
    if len(stdout) > 0 and len(stderr) > 0:
        stdout = stdout + "\n"
    if len(stdout) + len(stderr) > 0:
        output = f"  {indent}{stdout}{stderr}"
        output = output.replace("error",red("error")).replace("ERROR",red("ERROR"))
        # match and hilight any useful output from git, indicating incoming changes, or pushed changes
        # - [master 6946424] added/updated examples/workspace/terraform.auto.tfvars
        # - 1 file changed, 38 insertions(+)
        # - create mode 100644 examples/workspace/terraform.auto.tfvars
        # - adbd853..8f593eb  master     -> origin/master
        # - 64c8409..b096596  master -> master
        # - git add -f examples/workspace/terraform.auto.tfvars
        # - adding user's 'terraform.auto.tfvars' file
        # - git add -f examples/workspace/terraform.auto.tfvars
        if re.search('(.*added/updated.*|create mode|file changed,|master -> .*master|terraform.auto.tfvars)',output):
            output = cyan(output)
        output = output.replace("\n",f"\n  {indent}")
        result=f"{result}\n{output}"
    if process.returncode != 0:
        output = red(f"    {indent}ERROR: shell command '{cmd}' failed with return code '{process.returncode}'")
        result=f"{result}\n{output}"
        output = red(f"    {indent}       while in directory '{os.getcwd()}'")
        result=f"{result}\n{output}"
    return [ result.lstrip("\n"), process.returncode ]

# Execute "cmd" in a subprocess
# - Print the resulting output (unless quiet_flag==True)
# - Throws SubProcessRunError if quiet_flag==False and the shell command encountered an error
def subprocess_call(cmd:str, no_echo:bool = False, quiet_flag:bool = False):
    [output, returncode] = _subprocess_call(cmd, no_echo)
    if len(output) and not quiet_flag:
        print(output)
    if returncode != 0 and not quiet_flag:
        raise SubProcessRunError("Shell command failure")
    return returncode

# Execute "cmd" in a subprocess
# - Return the output as a string
def subprocess_call_output(cmd:str):
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True).decode('utf-8')

# Execute "cmd" in a subprocess
# - Return True if the process failed (False otherwise)
# - Don't print any output (unless quiet_flag==False)
def subprocess_call_fails(cmd:str, quiet_flag:bool = True):
    [output, returncode] = _subprocess_call(cmd, no_echo=quiet_flag)
    if len(output) and not quiet_flag:
        print(output)
    return returncode != 0

# Execute "cmd" in a subprocess
# - Return True if the process succeeds (False otherwise)
# - Don't print any output (unless quiet_flag==False)
def subprocess_call_succeeds(cmd:str, quiet_flag:bool = True):
    return(subprocess_call_fails(cmd, quiet_flag) == False)

# Print out info about the 'place' it was called from:
# - the filename, the line number, and the method name
def location_info():
    return f"File \"{os.path.basename(inspect.stack()[1][1])}\", line {inspect.stack()[1][2]}, in method \"{inspect.stack()[1][3]}()\""
