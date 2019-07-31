#!/usr/bin/env python3

import os
import sys
import json
import yaml
import subprocess
import shutil


task_dict = json.loads(sys.argv[1])

task_input = task_dict['input']
dockstore_tool = task_input['dockstore_tool']

cmd = "cwltool --make-template %s" % dockstore_tool
p = subprocess.run(cmd, capture_output=True, shell=True)

input_json = yaml.load(p.stdout, Loader=yaml.FullLoader)

for i in input_json:
    if i == 'run-id':
        input_json[i] = 'run-id'
    elif type(input_json[i]) in [str, int, bool]:
        input_json[i] = task_input[i]
    # cwltool make-template does not do good job with 'null' in template
    elif isinstance(input_json[i], list) and \
        isinstance(task_input[i], list) and \
        len(task_input[i]) > 0:  # a bit hacky here, assume it's a local file
        input_json[i] = []
        for f in task_input[i]:
            input_json[i].append(
                    {
                        'class': 'File',
                        'path': f
                    }
                )
    elif isinstance(input_json[i], dict) and input_json[i].get('class') in ['File', 'Directory']:
        input_json[i]['path'] = task_input[i]
    else:
        sys.exit('Required input not provided: %s' % i)

# write out the Job JSON for CWL tool
with open('job.json', 'w') as f:
    f.write(json.dumps(input_json, indent=2))

cwl_outdir = 'outdir'
if os.path.exists(cwl_outdir):  # remove  if exist
    shutil.rmtree(cwl_outdir)

os.makedirs(cwl_outdir)

# launch cwltool
cmd = "cwltool --non-strict --debug --outdir %s %s job.json" % (cwl_outdir, dockstore_tool)
p = subprocess.Popen( cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

stdout, stderr = p.communicate()

if p.returncode == 0:
    result = json.loads(stdout)

else: # cwltool run failed
    print(stderr, file=sys.stderr)
    sys.exit(p.returncode)

# parse stdout to get the parameters
output_dict = dict()

for key, val in result.items():
    if isinstance(val, str) or isinstance(val, int):
        output_dict[key] = val
    if isinstance(val, dict):
        output_dict[key] = val.get('path')
    if isinstance(val, list):
        output_dict[key] = []
        for v in val:
            output_dict[key].append(v.get('path'))

with open('output.json', 'w') as f:
    f.write(json.dumps(output_dict, indent=2))