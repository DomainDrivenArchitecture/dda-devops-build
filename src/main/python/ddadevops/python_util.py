from subprocess import check_output
import sys

def execute(cmd):
    if sys.version_info.major == 3:
        output = check_output(cmd, encoding='UTF-8')
    else:
        output = check_output(cmd)
    return output

def filter_none(list):
    return [x for x in list if x is not None]
