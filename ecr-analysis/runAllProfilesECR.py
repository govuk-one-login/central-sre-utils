# A Python script adapted from Dan's original script to run a boto3 AWS command in multiple AWS accounts.
# This script includes arguments for an AWS account name and an ecr repo name in order to extract relevant ECR data from each AWS account.
#This script is called by the bash script 'getRepoNames.sh'.

#!/usr/bin/env python3
from argparse import ArgumentParser
import boto3
import datetime
import json
import sys
import os

# Required to parse the AWS responses for datetimes
class DateTimeEncoder(json.JSONEncoder):

    def _preprocess_date(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime, datetime.timedelta)):
            return str(obj)
        elif isinstance(obj, dict):
            return {self._preprocess_date(k): self._preprocess_date(v) for k,v in obj.items()}
        elif isinstance(obj, list):
            return [self._preprocess_date(i) for i in obj]
        return obj

    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime, datetime.timedelta)):
            return str(obj)
        return super().default(obj)

    def iterencode(self, obj):
        return super().iterencode(self._preprocess_date(obj))

def logline(text, force=False):
    if args.verbose or force:
        print("[" + datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S") + "]\t" + text)

parser = ArgumentParser(description="Run a specified boto3 command against a specified boto3 client")
parser.add_argument("-s", "--service", dest="service",
                    help="(REQUIRED) \tThe AWS boto3 client you want to use, e.g. ec2")
parser.add_argument("-c", "--command", dest="command",
                    help="(REQUIRED) \tThe boto3 client command you want to call, e.g. describe_vpcs")
parser.add_argument("-f", "--filename", dest="filename", default="results.json",
                    help="(OPTIONAL) \tThe filename you want to write your results to. Defaults to results.json")
parser.add_argument("-r", "--region", dest="region", default="eu-west-2",
                    help="(OPTIONAL) \tThe AWS region you want to use. Defaults to eu-west-2")
parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                    help="(OPTIONAL) \tIncrease output verbosity")
parser.add_argument("-n", "--no-file", dest="nofile", action="store_true",
                    help="(OPTIONAL) \tWrite to screen instead of to file")
# Added an additional arg for the ECR repository name
parser.add_argument("-rn", "--repo-name", dest="reponame",
                    help="(OPTIONAL) \tThe repository name if you are listing ECR images")
# Added an additional arg for the AWS account name
parser.add_argument("-an", "--account-name", dest="accountname",
                    help="(OPTIONAL) \tThe account name you want to query")

args = parser.parse_args()
service = args.service
command = args.command
filename = args.filename
region = args.region
reponame = args.reponame
accountname = args.accountname

if args.service is None or args.command is None:
    print("ERROR: Missing one or more required args.")
    parser.print_help()
    sys.exit(1)

if service == "ecr" and command == "describe_images" and not reponame:
    print("ERROR: Repository name is required for describe_images command in ecr service.")
    parser.print_help()
    sys.exit(1)

logline("Started")
allResults = {}
try:
    logline("Account: " + accountname)
    session = boto3.Session(profile_name=accountname, region_name=region)
    client = session.client(service)
    # if we can use a paginator, we should
    if client.can_paginate(operation_name=command):
        paginator = client.get_paginator(command)
        if service == "ecr" and command == "describe_images":
            allResults[accountname] = paginator.paginate(repositoryName=reponame).build_full_result()
        else:
            allResults[accountname] = paginator.paginate().build_full_result()
    else: # no paginator available
        # dynamically call the command on the client
        func = getattr(client, command)
        if service == "ecr" and command == "describe_images":
            allResults[accountname] = paginator.paginate().build_full_result()
        else:
            allResults[accountname] = func()      
except Exception as e:
    logline("ERROR on account " + accountname, True)
    logline(str(e), True)

def append_json_to_file(filename, new_data):
    # Check if the file exists
    if os.path.exists(filename):
        # Read the existing content
        with open(filename, 'r') as file:
            try:
                # Parse the JSON content as a list
                data = json.load(file)
            except json.JSONDecodeError:
                # If the file is not a valid JSON, start with an empty list
                data = []
    else:
        # If the file does not exist, start with an empty list
        data = []

    # Append the new data
    data.append(new_data)

    # Write the updated list back to the file with pretty print
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4, cls=DateTimeEncoder)

# Print to console or write results to a file
if args.nofile:
    print(json.dumps(allResults, cls=DateTimeEncoder, indent=4))
else:
    if service == "ecr" and command == "describe_images":
        append_json_to_file(filename, allResults)
        logline("Appended to " + filename, force=True)
    else:
        with open(filename, 'w') as outfile:
            json.dump(allResults, outfile, cls=DateTimeEncoder, indent=4)
        logline("Written to " + filename, force=True)
