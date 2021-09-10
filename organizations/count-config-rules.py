import boto3 
import argparse

def count_config_rules(profile, region=None):
    session = boto3.Session(profile_name=profile)
    client = session.client('config', region_name=region) if region else session.client('config')
    paginator = client.get_paginator('describe_config_rules')
    page_iterator = paginator.paginate()
    total = 0
    for page in page_iterator:
        total += len(page["ConfigRules"])

    print(f'Total amount of config rules in {region} is {total}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', type=str, help="Input profile name", required=True)
    parser.add_argument('--region', type=str, help='Input region')
    args = parser.parse_args()

    count_config_rules(args.profile, region=args.region)