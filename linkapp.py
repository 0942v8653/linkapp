#!/usr/bin/env python

import sys

if len(sys.argv) <= 2:
    printerr("Usage: linkapp.py <app-bundle> <new-place>\n")
    exit(1)

import os
import shutil
import subprocess
import re

WRAPPER_SCRIPT = '''\
#!/usr/bin/env bash
executable="$(dirname "$0")/%s"

# add flags here.
"$executable" 
'''

def printerr(message):
    sys.stderr.write("\033[1;31m" + message + "\033[0m")
    
def link_item(item):
    os.symlink(os.path.join(bundle_contents_path, item),
               os.path.join('.', item))

def replace_executable(filename, new_executable):
    old_executable = subprocess.check_output(['defaults', 'read', os.path.abspath(filename), 'CFBundleExecutable'])
    old_executable = old_executable.rstrip()
    subprocess.call(['defaults', 'write', os.path.abspath(filename), 'CFBundleExecutable', new_executable])
    return old_executable

bundle_path = os.path.abspath(sys.argv[1])
bundle_contents_path = os.path.join(bundle_path, 'Contents')
new_contents_path = os.path.abspath(os.path.join(sys.argv[2], 'Contents'))
os.makedirs(new_contents_path)

# loop through the app bundle and symlink everything
#                                        (except Resources, MacOS & Info.plist)
os.chdir(new_contents_path)
for i in os.listdir(bundle_contents_path):
    if i.lower() != 'info.plist':
        if i.lower() in ['resources', 'macos']:
            os.makedirs(i)
            for j in os.listdir(os.path.join(bundle_contents_path, i)):
                link_item(os.path.join(i, j))
        else:
            link_item(i)

# just copy Info.plist for easy editing
shutil.copy(os.path.join(bundle_contents_path, 'Info.plist'), new_contents_path)
subprocess.call(['plutil', '-convert', 'xml1', 'Info.plist'])

printerr("Create wrapper script [y/n]? ")
ans = sys.stdin.read(1)
if ans.lower() == 'y':
    os.chdir('MacOS')
    
    wrapper_script_file = 'run_with_specified_arguments.sh'
    
    original_executable = replace_executable('../Info.plist', wrapper_script_file)
    
    with open(wrapper_script_file, 'w') as f:
        f.write(WRAPPER_SCRIPT % original_executable)
    os.chmod(wrapper_script_file, 0755)
    
    subprocess.call(['open', '-R', wrapper_script_file])
