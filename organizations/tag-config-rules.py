import boto3 

session = boto3.Session(profile_name="ni")

client = session.client('config')

paginator = client.get_paginator('describe_config_rules')
page_iterator = paginator.paginate()

for page in page_iterator:
    for rule in page['ConfigRules']:
        print(rule['ConfigRuleName'])
        if 'securityhub' not in rule['ConfigRuleName']:
            response = client.list_tags_for_resource(ResourceArn=rule['ConfigRuleArn'])
            if len(response['Tags'])==0:
                client.tag_resource(
                    ResourceArn=rule['ConfigRuleArn'],
                    Tags=[
                        {
                            "Key": "compliance",
                            "Value": "security"
                        },
                    ]
                )   
            print('add tag')
        else:
            print('security hub rule')
