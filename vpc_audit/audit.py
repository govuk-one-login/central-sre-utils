import sys
import boto3
import re
from boto3 import client

def main():
        
    accounts = get_accounts()
    vpc_stack_info = []
    
    stack_exceptions = [
       'vpctest-far-ci', # di-devplatform-build-demo-sre-vpc-readonly
       'plat-3005-vpc' # di-devplatform-development-sre-vpc-readonly
    ]
    
    for account in accounts:
        print(account)
        client = get_cf_client(account)

        vpc_dict = {'account': account}
        get_vpc_stack_name_and_version(stacks_list=get_all_stacks(cf_client=client), vpc_dict=vpc_dict)
        if 'stack_name' in vpc_dict.keys() and vpc_dict['stack_name'] not in stack_exceptions:
            get_vpc_stack_params(cf_client=client, vpc_dict=vpc_dict)
            vpc_stack_info.append(vpc_dict)
            
    with open('findings.jsonl', 'w') as f:
        for item in vpc_stack_info:
            f.write(f"{item}\n")
    
        
def get_vpc_stack_params(cf_client: client, vpc_dict: dict):
    params = cf_client.describe_stacks(StackName=vpc_dict['stack_name'])['Stacks'][0]['Parameters']
    params_dict = {}
    for param in params:
        params_dict.update({param['ParameterKey']: param['ParameterValue']}) 
    
    vpc_dict['parameters'] = params_dict
     
    return vpc_dict
      
        
def get_cf_client(profile: str):
    print(f'MELV MELV MELV {profile}')
    session = boto3.Session(profile_name=profile, region_name='eu-west-2')
    
    # print(session.client('sts').get_caller_identity())
    
    return session.client('cloudformation')
    
def get_all_stacks(cf_client: client) -> list:
        """
        Get all stacks in the account.

        :param cf_client: CloudFormation implemntation of Client.
        :type cf_client: dict
        :return: List of dictionaries describing deployed CloudFormation stacks.
        :rtype: list
        """
        
        response_stacks = cf_client.list_stacks()
        list_of_all_stacks = response_stacks['StackSummaries']
        
        if 'NextToken' in response_stacks.keys():
            try:    
                while response_stacks['NextToken'] is not None:
                    response_stacks = cf_client.list_stacks(NextToken=response_stacks['NextToken'])
                    list_of_all_stacks.extend(response_stacks['StackSummaries'])
            except KeyError:
               list_of_all_stacks.extend(response_stacks['StackSummaries'])
            
        return list_of_all_stacks
    
def get_vpc_stack_name_and_version(stacks_list: list, vpc_dict = {}):
    
    for stack in stacks_list:
        if 'TemplateDescription' in stack.keys() and 'devplatform-deploy' in stack['TemplateDescription'] and 'vpc' in stack['TemplateDescription']:
            extracted_version_matcher = re.search('version: v[0-9]+\.[0-9]+\.[0-9]+', stack['TemplateDescription'])
            extracted_template_version = extracted_version_matcher.group(0).split(' ')[1]
            
            vpc_dict['stack_name'] = stack['StackName']
            vpc_dict['version_number'] = extracted_template_version
            return vpc_dict
        
    
def get_accounts():
    
    accounts = []
    
    with open('accounts.txt') as file:
        while account := file.readline():
            accounts.append(account.rstrip())
    
    return accounts
            
    
if __name__ == "__main__":
    sys.exit(main())