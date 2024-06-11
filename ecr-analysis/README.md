# Get current image counts / dates / usage per AWS account

## Prerequisites

`aws cli` installed (https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

`jq` installed (https://jqlang.github.io/jq/download/)

`python3` installed

`boto3` Python package installed

## Setup

### Run 'addAccountsToConfig.sh' script

The `get-sso-accounts.sh` script will auto-populate your `~/.aws/config` with profiles for all the accounts you have access to via SSO.

This is especially useful if you require temporary access to accounts to complete a specific piece of work, as you can quickly update your config based on your current permissions, then either restore a backed-up version of your config, or blow your config away completely and start again.

### Configure AWS SSO

AWS SSO configured: Run `aws configure sso` and follow the instructions. See https://docs.aws.amazon.com/cli/latest/userguide/sso-configure-profile-token.html#sso-configure-profile-token-auto-sso for more information.

An active AWS SSO session: Run `aws sso login --profile <your-profile-name>`
It doesn't matter which profile you choose, any profile you have will work. 
If you don't know what profile to use, look at your aws config and pick a profile from there (e.g. `cat ~/.aws/config`)

## Scripts

The order in which scripts should be run is:
1. runAllProfiles.py
2. getRepoNames.sh
3. [optional] analyseJson.py

### runAllProfiles.py script

This script was originally written by Dan Sparks and can be found here: (https://github.com/govuk-one-login/central-sre-utils/blob/SW-117-runAllProfiles.py/runAllProfiles.py).
In the context of retrieiving ECR image data, this script needs to be run first to retrieve the ECR repositories in each account. The ECR images can then be retrieved by specifying the names of the repositories in each account.
The command to describe the ECR repositories in each account: 'python3 runAllProfiles.py -s ecr -c describe_repositories -r eu-west-2 -f accountRepositories.json'
The 'accountRepositories.json' file created is used in the next script 'getRepoNames.sh'

### getRepoNames.sh 

This script iterates through the AWS account names and repo names in the 'accountRepositories.json' file and runs the 'runAllProfilesECR.py' script, to retreive specific image details from the ECR repos of each AWS account.
The command to run this script is '/bin/bash getRepoNames.sh'.
The 'describeImages.json' file created lists all the ECR image details for each ECR repo in each AWS account.

### [OPTIONAL] analyseJson.sh

This script counts the total number of images in each AWS account, the number of image versions in each ECR repo and formats it into a text file.