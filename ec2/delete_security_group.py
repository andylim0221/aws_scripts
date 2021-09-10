import boto3 
import argparse
import inquirer
import time
import re
from pprint import pprint

my_parser = argparse.ArgumentParser(description="remove bucket")
my_parser.add_argument('--profile', type=str, help="profile to be used")



def main():
    args = my_parser.parse_args()
    profile = args.profile
    session = boto3.Session(profile_name=profile)

    client = session.client('ec2')

    res = client.describe_security_groups()
    sgs = [sg['GroupId'] for sg in res['SecurityGroups']]


    questions = [
    inquirer.Checkbox('sgs',
                      message="Which security groups are you going to delete?",
                      choices=sgs
                      ),
    inquirer.Text('confirm',
                    message="Are you sure you want to delete the buckets? Type delete to confirm your actions",
                    validate=lambda _, x: re.match('^delete$', x)
                    )
    ]

    answer = inquirer.prompt(questions)
    print(answer)
    if len(answer['sgs'])>0 and answer['confirm'] == 'delete':          
        for sg in answer['sgs']:
            print(f'deleting sg {sg}...')
            client.delete_security_group(GroupId=sg)
            time.sleep(3)


if __name__ == '__main__':
    main()
