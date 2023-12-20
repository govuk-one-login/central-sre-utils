import sys
import boto3
import re
from boto3 import client

def main():
        
    vpc_stack_info = []
    
    stack_exceptions = [
       'vpctest-far-ci', # di-devplatform-build-demo-sre-vpc-readonly
       'plat-3005-vpc' # di-devplatform-development-sre-vpc-readonly
    ]
    
    for profile in get_profiles():
        print(profile)
        
        session = boto3.Session(profile_name=profile, region_name='eu-west-2')
        ec2_client = session.client('ec2')
        
        ip_tally = get_elb_address_count(ec2_client=ec2_client)
        ip_tally = ip_tally + describe_instances(ec2_client=ec2_client)
        ip_tally = ip_tally + nat_gateway_count(ec2_client=ec2_client)
        ip_tally = ip_tally + network_interfaces_count(ec2_client=ec2_client)
        
        ecs_client = session.client('ecs')
        ecs_resources(ecs_client=ecs_client,tally=ip_tally)
        
        rds_client = session.client('rds')
        ip_tally = ip_tally + len(rds_client.describe_db_instances()['DBInstances'])
        
        lambda_client = session.client('lambda')
        ip_tally = ip_tally + lambda_saturation_count(lambda_client=lambda_client)
        
        vpc_dict = {'account': profile.replace('-sre-vpc-readonly', ''), 'ip_usage_approximation': ip_tally}
        
        cf_client = session.client('cloudformation')
        
        list_of_all_stacks=[]
        
        get_all_stacks(cf_client=cf_client, response_stacks=cf_client.list_stacks(), list_of_all_stacks=list_of_all_stacks)
        
        get_vpc_stack_name_and_version(stacks_list=list_of_all_stacks, vpc_dict=vpc_dict)
        if 'stack_name' in vpc_dict.keys() and vpc_dict['stack_name'] not in stack_exceptions:
            get_vpc_stack_params(cf_client=cf_client, vpc_dict=vpc_dict)
            
        vpc_stack_info.append(vpc_dict)
            
    with open('findings.jsonl', 'w') as f:
        for item in vpc_stack_info:
            item_as_str = str(item).replace('"', '\\"')
            item_as_str = item_as_str.replace('\'', '"')
            f.write(f"{item_as_str}\n")

def lambda_saturation_count(lambda_client: client) -> int:
    
    function_names = []
    
    response = lambda_client.list_functions(MaxItems=50)
    process_list_functions(lambda_client=lambda_client, response=response,function_names=function_names)
    
    tally = 0
    iteration = 0
    
    for function_name in function_names:
        iteration += 1
        
        
        if 'AWSAccelerator' in function_name or 'aws-controltower' in function_name:
            tally += 1 
        else: 
            print('MELV MELV MELV')
            print(function_name)
            print(lambda_client.get_function_concurrency(FunctionName=function_name))
            try:
                tally = tally + lambda_client.get_function_concurrency(FunctionName=function_name)['ReservedConcurrentExecutions']
            except KeyError:
                if tally == 0:
                    average = 10
                else:
                    average = round(tally/iteration)
                    if average < 10:
                        average = 10
                tally = tally + average
            
    return tally
    
            
def process_list_functions(lambda_client: client, response: dict, function_names: list) -> None:
    
    for function in response['Functions']:
        function_names.append(function['FunctionName'])
    
    if 'NextMarker' in response.keys():
        response = lambda_client.list_functions(MaxItems=50, Marker=response['NextMarker'])
        process_list_functions(lambda_client=lambda_client, response=response, function_names=function_names)
 
def ecs_resources(ecs_client: client, tally: int):
    cluster_arns = ecs_client.list_clusters(maxResults=100)['clusterArns']
    for cluster_arn in cluster_arns:
         ecs_task_count(
             ecs_client=ecs_client,
             tasks=ecs_client.list_tasks(cluster=cluster_arn),
             cluster_arn=cluster_arn,
             tally=tally)
    

def ecs_task_count(ecs_client: client, tasks: dict, cluster_arn: str, tally: int):
    
    tally = tally + len(tasks['taskArns'])
    
    if 'nextToken' in tasks.keys():
        ecs_task_count(
            ecs_client=ecs_client,
            tasks=ecs_client.list_tasks(nextToken=tasks['nextToken'],
                                        cluster=cluster_arn),
            cluster_arn=cluster_arn,
            tally=tally)
    

def get_elb_address_count(ec2_client: client):
    return len(ec2_client.describe_addresses()['Addresses'])

def describe_instances(ec2_client: client):
    
    return_count = 0
    
    reservations = ec2_client.describe_instances()['Reservations']
    
    for reservation in reservations:    
        if 'Instances' in reservation.keys():
            return_count = return_count + len(reservation['Instances'])
                
    return return_count

def nat_gateway_count(ec2_client: client):
    return len(ec2_client.describe_nat_gateways()['NatGateways'])

def network_interfaces_count(ec2_client: client):
    return len(ec2_client.describe_network_interfaces()['NetworkInterfaces'])
        
def get_vpc_stack_params(cf_client: client, vpc_dict: dict):
    params = cf_client.describe_stacks(StackName=vpc_dict['stack_name'])['Stacks'][0]['Parameters']
    params_dict = {}
    for param in params:
        params_dict.update({param['ParameterKey']: param['ParameterValue']}) 
    
    vpc_dict['parameters'] = params_dict
     
    return vpc_dict
    
def get_all_stacks(cf_client: client, response_stacks: dict, list_of_all_stacks: list):

        list_of_all_stacks.extend(response_stacks['StackSummaries'])        
        if 'NextToken' in response_stacks.keys():
            get_all_stacks(cf_client=cf_client,
                           response_stacks=cf_client.list_stacks(NextToken=response_stacks['NextToken']),
                           list_of_all_stacks=list_of_all_stacks)
    
def get_vpc_stack_name_and_version(stacks_list: list, vpc_dict = {}):
    
    for stack in stacks_list:
        if 'TemplateDescription' in stack.keys() and 'devplatform-deploy' in stack['TemplateDescription'] and 'vpc' in stack['TemplateDescription']:
            extracted_version_matcher = re.search('version: v[0-9]+\.[0-9]+\.[0-9]+', stack['TemplateDescription'])
            extracted_template_version = extracted_version_matcher.group(0).split(' ')[1]
            
            vpc_dict['stack_name'] = stack['StackName']
            vpc_dict['version_number'] = extracted_template_version
            return vpc_dict
        
    
def get_profiles():
    
    profiles = []
    
    with open('profiles.txt') as file:
        while profile := file.readline():
            profiles.append(profile.rstrip())
    
    return profiles
            
    
if __name__ == "__main__":
    sys.exit(main())