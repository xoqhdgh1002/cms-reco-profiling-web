import json
import os
import sys

# find the json file
filelist = []
for root, dirs, files in os.walk('/eos/project-c/cmsweb/www/reco-prof/circles/data/'):
    for file in files:
        if file.endswith('circles.json'):
            filelist.append(os.path.join(root, file))

print(filelist)

# read the json file
for file in filelist:
    with open(file, 'r') as f:
        data = json.load(f)
        #print(data['modules'])
        for line in data['modules']:
            if line['label'] == 'source' or line['label'] == 'AODSIMoutput':
                # drop the module
                data['modules'].remove(line)
        
        # save the json file
        with open(file, 'w') as f:
            json.dump(data, f, indent=4)

