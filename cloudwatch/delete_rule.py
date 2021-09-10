import boto3
import argparse

my_parser = argparse.ArgumentParser(description="remove event rule")
my_parser.add_argument('--rule', type=str, help="rule name to be removed")
my_parser.add_argument('--region', type=str, help="region of rule name")
my_parser.add_argument('--profile', type=str, help="profile to be used")


def main():
    args = my_parser.parse_args()
    rule = args.rule
    region = args.region
    profile = args.profile
    session = boto3.Session(profile_name=profile)
    client = session.client('events', region_name=region)

    response = client.list_targets_by_rule(Rule=rule)
    targets = [x['Id'] for x in response['Targets']]
    if targets:
        err = client.remove_targets(Rule=rule, Ids=targets)
        failed_entries = err['FailedEntries']
        if failed_entries:
            print(err)
            return
    client.delete_rule(Name=rule)
    print(f'Remove event rule {rule} successfully')

if __name__ =="__main__":
    main()





