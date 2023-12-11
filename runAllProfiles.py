from argparse import ArgumentParser
import boto3
import datetime
import json
import sys

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



args = parser.parse_args()
service = args.service
command = args.command
filename = args.filename
region = args.region

if args.service is None or args.command is None:
    print("ERROR: Missing one or more required args.")
    parser.print_help()
    sys.exit(1)

logline("Started")
allResults = {}
for profile in boto3.session.Session().available_profiles:
    try:
        logline("Profile: " + profile)
        session = boto3.Session(profile_name=profile, region_name=region)
        
        client = session.client(service)
        func = getattr(client, command)
        allResults[profile] = func()
    except Exception as e:
        logline("ERROR on profile " + profile, True)
        logline(str(e), True)
if args.nofile:
    print(json.dump(allResults, sys.stdout, cls=DateTimeEncoder))
else: 
    with open(filename, "w") as outfile: 
        json.dump(allResults, outfile, cls=DateTimeEncoder) 
    logline("Written to " + filename)
