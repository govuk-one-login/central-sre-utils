#!/bin/bash -e



# How to use this script:
# 1. Follow these instructions to configure a single AWS account to do initial login with SSO
#    https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html
# 2. Export AWS_PROFILE=... and then run "aws sso login" to get an SSO token
# 3. Once signed in with AWS SSO, run this script to automatically list out all the other accounts and roles and add them to your config file

# If you want to filter roles / accounts in the process, or validate config before committing it, you can customise the script to do this.

rm -rf ~/.aws/config_append
at_filename=$(ls -t ~/.aws/sso/cache/*.json | grep -v botocore | head -n 1)
at=$(cat $at_filename | jq -r '.accessToken')
start_url=$(cat $at_filename | jq -r '.startUrl')
region_sso=$(cat $at_filename | jq -r '.region // "us-east-1"')

# alter this line if you prefer to work in a specific region
# e.g. assume_role_region=eu-west-2
assume_role_region=$region_sso

if [[ "$at" =~ "null" ]] ; then
    echo "No access token found. Did you remember to run 'aws sso login' first?" ;
fi

# Iterate account list
available_accounts=$(aws sso list-accounts --region "$region_sso" --access-token "$at")
n_accounts=$(echo $available_accounts | jq '.accountList | length')
echo "Accounts found: $n_accounts"

account_list=$(echo $available_accounts | jq -r '.accountList | .[] | .accountId')

while IFS= read account_id ; do
    echo "account: $account_id"
    account_data=$( echo $available_accounts | jq -r ".accountList | .[] | select( .accountId == \"$account_id\" )" )
    account_name=$(echo $account_data | jq -r '.accountName // .accountId' | xargs | tr -d "[:space:]")
    account_roles=$(aws sso list-account-roles --region "$region_sso" --access-token "$at" --account-id $account_id)
    role_names=$(echo $account_roles | jq -r '.roleList | .[] | .roleName')
    while read role_name ; do
        echo "  role: $role_name"
        config_profile_name="$account_name-$role_name"
        hit=$(cat ~/.aws/config | grep $config_profile_name || echo "")
        if [ -z "$hit" ] ; then
            echo "    profile: $config_profile_name not found, adding to config..."
            cat << EOF >> ~/.aws/config_append
[profile $config_profile_name]
sso_start_url = $start_url
sso_region = $region_sso
sso_account_id = $account_id
sso_role_name = $role_name
sts_regional_endpoints = regional
region = $assume_role_region
EOF
        else
            echo "    profile: $config_profile_name found, doing nothing..."
        fi
    done < <(printf '%s\n' "$role_names")
done < <(printf '%s\n' "$account_list")

echo ""
echo ""
echo "The following config will be appended to your ~/.aws/config file:"
cat ~/.aws/config_append
echo ""
read -p "Do want to proceed? [y/n] " yn
case $yn in
    [Yy]* ) cat ~/.aws/config_append >> ~/.aws/config; echo "committed!"; ;;
    * ) echo "cancelled!";;
esac
echo "cleaning up..."
rm ~/.aws/config_append
echo "Done!"

