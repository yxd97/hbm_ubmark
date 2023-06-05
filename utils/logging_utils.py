import os
import sys

def pinfo(*args, **kwargs):
    print("[INFO] ", *args, **kwargs, file=sys.stdout)

def pwarning(*args, **kwargs):
    print("[WARNING] ", *args, **kwargs, file=sys.stdout)

def perror(*args, **kwargs):
    print("[ERROR] ", *args, **kwargs, file=sys.stderr)

def echo_chdir(dir:str):
    pinfo(f'changing to directory {dir}')
    os.chdir(dir)