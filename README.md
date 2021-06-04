# Vault User Creator

A simple python3 script to create user on Hashicorp Vault, using the userpass auth method.

## Configuring

Create a file called `users.yaml` on the repository folder and add the users as a list
```yaml
- user1
- user2
```
They can also have a list of policies
```yaml
- user1:
  - policy1
  - policy2
- user2:
  - policy3
- user3
```

If no policy is given, a default policy list will be used for that user, 
you can change this policy list by edit the following line on `script.py`
```python
...
# Edit to change the default policies list if no policy list is provided on users.yaml
DEFAULT_POLICIES = ['developer']
...
```

## How to use

Install the requirements (requires pip3 installed)
```
make install
```

Execute the following command
```
python3 script.py
```

Output example
```
$ python3 script.py 
Username: test1
Password: !8W0G9f#z$P6DpwJ
Policies: ['developer', 'prod-access']
User created successfully!

Username: test2
Password: gN6vhKPLq#rp4mBE
Policies: ['developer']
User created successfully!

User davi already exists. Skipping...
```