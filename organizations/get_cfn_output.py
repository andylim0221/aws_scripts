import csv
from basic import session
from disable_cis_in_sandbox import list_accounts_by_ou 
import time
import argparse

def find_stack_output(keyword):
    try:
        client = session.client("cloudformation",
                region_name = 'us-east-1',
                aws_access_key_id = access_key,
                aws_secret_access_key = secret_key,
                aws_session_token = access_token
                )
        response = client.list_stacks()
        for stack in response["StackSummaries"]:
            if keyword in stack["StackName"]:
                print(stack["StackName"])
                output = client.describe_stacks(StackName=stack["StackName"])
                return output["Stacks"][0]["Outputs"][0]["OutputValue"]

    except Exception as e:
        print(e)

def handler(ou_id, keyword):
    sts = session.client('sts')
    global access_key 
    global secret_key
    global access_token

  # change this for different OU
    page_iterator = list_accounts_by_ou(ou_id)

    with open(f'example{int(time.time())}.csv', mode='w') as csv_file:
        fieldnames = ['Name', 'AccountId', 'ARN']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for page in page_iterator:
            for acct in page["Accounts"]:
                try:
                    sts_r = sts.assume_role(
                        RoleArn = f"arn:aws:iam::{acct['Id']}:role/AWSControlTowerExecution",
                        RoleSessionName = "check-cfn-output"
                    )

                    access_key = sts_r["Credentials"]["AccessKeyId"]
                    secret_key = sts_r["Credentials"]["SecretAccessKey"]
                    access_token = sts_r["Credentials"]["SessionToken"]
                except Exception as e:
                    print(e)
                else:
                    arn = find_stack_output(keyword)
                    row = {'Name':acct['Name'], 'AccountId': str(acct['Id']), 'ARN': str(arn)}
                    writer.writerow(row)   
                    
if __name__ == "__main__":
    parser = argparse.ArgumentParser
    parser.add_argument('--ou',
        type=str,
        required=True
    )
    parser.add_argument('--keyword',
        type=str,
        required=True    
    )
    args = parser.parse_args()
    handler(args.ou_id,args.keyword)
