#A bash script to iterate through AWS accounts, extract the ECR repo names and describe the images within them

#!/bin/bash

# Define the path to the JSON file
json_file="accountRepositories.json"

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "jq is not installed. Please install it and try again."
    exit 1
fi

# Iterate through the top-level keys
account_names=$(jq -r 'keys[]' "$json_file")

# Loop through each account name and extract repository names
for account in $account_names; do
    echo "Account: $account"
    repository_names=$(jq -r --arg account "$account" '.[$account].repositories[].repositoryName' "$json_file")
    # Check if the extraction was successful
    if [ -z "$repository_names" ]; then
        echo "Failed to extract repository names from $json_file"
        exit 1
    fi
    # Loop through repos in the account
    for repo_name in $repository_names; do
        echo "  Repository Name: $repo_name"
        echo "---------------------"

        # Iterate through the repo's and run the command for runAllProfilesECR.py script to describe the images in the repo
        command="python3 runAllProfilesECR.py -s ecr -c describe_images -r eu-west-2 -f describeImages.json -rn $repo_name -an $account"
        $command
        echo "python script run for account name $account and repo name $repo_name"
    done
done