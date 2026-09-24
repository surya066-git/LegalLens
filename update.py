import json

with open('trigger.json', 'r', encoding='utf-16') as f:
    d = json.load(f)

d['build']['steps'][1] = {
    'id': 'Build',
    'name': 'gcr.io/k8s-skaffold/pack',
    'entrypoint': 'pack',
    'args': [
        'build', 
        '$_AR_HOSTNAME/$_AR_PROJECT_ID/$_AR_REPOSITORY/$REPO_NAME/$_SERVICE_NAME:$COMMIT_SHA', 
        '--builder=gcr.io/buildpacks/builder:v1', 
        '--path=services/api'
    ]
}

d['build']['steps'][2]['args'] = [
    'push',
    '$_AR_HOSTNAME/$_AR_PROJECT_ID/$_AR_REPOSITORY/$REPO_NAME/$_SERVICE_NAME:$COMMIT_SHA'
]

with open('trigger_updated.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2)
