import boto3
import argparse

my_parser = argparse.ArgumentParser(description="remove event rule")
my_parser.add_argument('--key', type=str, help="private key")
my_parser.add_argument('--region', type=str, help="")
my_parser.add_argument('--subnet', type=str, help="")
names = ['/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2']

def main():
    args = my_parser.parse_args()
    region = args.region
    key_name = args.key
    subnet = args.subnet

    if region:
        ec2_client = boto3.client('ec2', region_name=region) 
        ssm = boto3.client('ssm', region_name=region)
    else:
        ec2_client = boto3.client('ec2')
        ssm = boto3.client('ssm')

    response = ssm.get_parameters(Names=names)
    metadata = response['ResponseMetadata']
    if metadata['HTTPStatusCode'] == 200:
        params = response['Parameters']
        ami = [p.get('Value') for p in params][0]
        res = ec2_client.run_instances(ImageId=ami, InstanceType="t2.micro", KeyName=key_name, MaxCount=1, MinCount=1, SubnetId="subnet-0ebab4991b4a3add9")
        instances = res['Instances']
        instance_ids = [i.get('InstanceId') for i in instances]
        print(instance_ids)

if __name__ == "__main__":
    main()
