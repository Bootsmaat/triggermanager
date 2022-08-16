import json

def save(file, data):
    with open(file, 'w') as wf:
        json.dump(data, wf, indent=4)
    
def load(file):
    data = None

    with open(file, 'r') as rf:
        data = json.load(rf)

    return data