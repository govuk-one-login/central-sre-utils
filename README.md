# central-sre-utils

## Setup

### MacOS & zsh

To add these scripts to your `$PATH` so you can run them without providing the full path to the script each time:

1. `cd` to the root of this repository's directory

2. Run
```
echo -n "typeset -U path \npath=($(pwd) \$path)\n" > ~/.zlogin
source ~/.zlogin
```

(Only run this once or you'll keep appending to your ~/.zlogin file!)
