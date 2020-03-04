from subprocess import check_output
import sys

def execute(cmd, shell=False):
    if sys.version_info.major == 3:
        output = check_output(cmd, encoding='UTF-8', shell=shell)
    else:
        output = check_output(cmd, shell=shell)
    return output.rstrip()

def filter_none(list):
    return [x for x in list if x is not None]
