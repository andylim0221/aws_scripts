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
    
    client = session.client('s3')
    s3 = session.resource('s3')

    res = client.list_buckets()
    buckets = [bucket['Name'] for bucket in res['Buckets']]


    questions = [
    inquirer.Checkbox('buckets',
                      message="Which buckets are you going to delete?",
                      choices=buckets
                      ),
    inquirer.Text('confirm',
                    message="Are you sure you want to delete the buckets? Type delete to confirm your actions",
                    validate=lambda _, x: re.match('^delete$', x)
                    )
    ]

    answer = inquirer.prompt(questions)
    print(answer)
    if len(answer['buckets'])>0 and answer['confirm'] == 'delete':          
        for bucket in answer['buckets']:
            print(f'deleting objects in bucket {bucket}...')
            content = client.list_objects(Bucket=bucket)
            if 'Contents' in content and len(content['Contents'])>0:
                objects = [{'Key':object['Key']} for object in content['Contents']]
                client.delete_objects(Bucket=bucket,Delete={'Objects':objects})
                time.sleep(3)
            
            print(f'removing object versions...')
            
            versions = client.list_object_versions(Bucket=bucket)
            if 'Versions' in versions and len(versions['Versions'])>0:
                s3_bucket = s3.Bucket(bucket)
                s3_bucket.object_versions.delete()
                time.sleep(1)
               
            print(f'deleting bucket {bucket}...')
            client.delete_bucket(Bucket=bucket)
            time.sleep(3)


if __name__ == '__main__':
    main()