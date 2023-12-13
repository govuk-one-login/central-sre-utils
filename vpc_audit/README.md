Add a list of accounts into accounts.txt that you have permission to query cloudformation in.

However you configure your python environment install boto3 

```bash
pip install boto3   
```

Assume any role with sso

run it
```bash
cd vpc_audit
python audit.py
```