# central-sre-utils

## Setup

### MacOS & zsh

To add these scripts to your `$PATH` so you can run them without providing the full path to the script each time:

1. `cd` to the root of this repository's directory

2. Run `echo -n "typeset -U path \npath=($(pwd) \$path)\n" > ~/.zlogin`

3. Run `source ~/.zlogin` to 

*You should only follow these steps once - running them again will add duplicate lines to your `~/.zlogin` file!*


## Scripts

### get-sso-accounts.sh

The `get-sso-accounts.sh` script will auto-populate your `~/.aws/config` with profiles for all the accounts you have access to via SSO.

This is especially useful if you require temporary access to accounts to complete a specific piece of work, as you can quickly update your config based on your current permissions, then either restore a backed-up version of your config, or blow your config away completely and start again. 

It would be nice if the script offered to back up your current config for you; feel free to submit a PR that implements this!

#### Prerequisites

`aws cli` installed (https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

`jq` installed (https://jqlang.github.io/jq/download/)

AWS SSO configured: Run `aws configure sso` and follow the instructions. See https://docs.aws.amazon.com/cli/latest/userguide/sso-configure-profile-token.html#sso-configure-profile-token-auto-sso for more information.

An active AWS SSO session: Run `aws sso login --profile <your-profile-name>`
It doesn't matter which profile you choose, any profile you have will work. 
If you don't know what profile to use, look at your aws config and pick a profile from there (e.g. `cat ~/.aws/config`)

#### Running the script

Assuming you've followed the Setup instructions, open a terminal and run `get-sso-accounts.sh`

Follow the prompts; if accounts are found that don't exist in your aws config you'll be asked if you want to add those accounts. Choose `y` (or `Y`) to add - any other input will cancel the process.

#### Troubleshooting

`zsh: command not found: get-sso-accounts.sh`
- Make sure you've followed the Setup instructions
- If you've *just* followed the Setup instructions, make sure you've run `source ~/.zlogin` (or open a new terminal).
- If you keep getting this error, it's possible there are some issues with your $PATH. In a pinch, you can provide a path to the script and run it that way instead:

*From the repository root:*
`./get-sso-accounts.sh`

*From anywhere else:*
`/Users/user.name/path/to/repository/get-sso-accounts.sh`

---
`An error occurred (UnauthorizedException) when calling the ListAccounts operation: Session token not found or invalid`

- Your AWS SSO session has likely expired. 
- Run `aws sso login --profile <your-profile-name>` and then try again.

---
`No such file or directory` or `No access token found. Did you remember to run 'aws sso login' first?`

- There are no cached files for your AWS SSO session in the default location. 
- Run `aws sso login --profile <your-profile-name>` and then try again.

---
