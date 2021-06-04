import os
import yaml
import random
import string
import hvac
from termcolor import cprint

# Edit to change the default policies list if no policy list is provided on users.yaml
DEFAULT_POLICIES = ['developer']

AVAILABLE_POLICIES = []

class User:
    name = None
    password = None
    
    def __init__(self):
        self.policies = DEFAULT_POLICIES.copy()

    def format_user(self, unformatted_user):
        if type(unformatted_user) is not dict:
            self.name = unformatted_user
        else:
            self.name = list(unformatted_user.keys())[0]
            policies = list(unformatted_user.values())[0]
            check_policies(policies)
            self.policies = policies
    
    def __str__(self):
        out = f"Username: {self.name}\nPassword: {self.password}\nPolicies: {self.policies}"
        return out


def password_generator(length=16):
    special_chars = '!@#$%^&*'
    combination = string.ascii_letters + string.digits + special_chars
    return "".join(random.sample(combination,length))

def get_users():
    cwd = os.getcwd()
    if cwd[-1] != '/':
        cwd += '/'
    with open(cwd + 'users.yaml', mode='r') as file:
        users = yaml.load(file, Loader=yaml.FullLoader)
        return users

def check_policies(policy_list: list):
    for policy in policy_list:
        if policy not in AVAILABLE_POLICIES:
            message = f"The policy {policy} is not on available policies."
            message += f"\nAvailable Policies: {AVAILABLE_POLICIES}"
            raise Exception(message)

def get_formated_users():
    users = get_users()
    result = list()
    for unformatted_user in users:
        formated_user = User()
        formated_user.format_user(unformatted_user)
        result.append(formated_user)
    
    return result

def vault_client():
    vault_url = os.getenv("VAULT_ADDR")

    client = hvac.Client(url=vault_url)
    if not client.is_authenticated():
        raise Exception("You are not authenticated, please log in!")
    return client

def get_existent_users(client: hvac.Client):
    return client.auth.userpass.list_user()['data']['keys']

def create_users(client: hvac.Client, users: list):
    for user in users:
        if user.name in get_existent_users(client):
            cprint(f"User {user.name} already exists. Skipping...\n", "yellow")
        else:
            user.password = password_generator()
            response = client.auth.userpass.create_or_update_user(
                username=user.name,
                password=user.password,
                policies=user.policies
            )
            if response.status_code == 200 or response.status_code == 204:
                print(user)
                cprint(f"User created successfully!\n", "green")
            else:
                msg = "There was an error on creating the user."
                msg += f"Status code: {response.status_code}. "
                msg += f"Response message: {response.text}"
                cprint(msg, "red")

def get_available_policies(client):
    given = set(client.sys.list_policies()['data']['policies'])
    to_remove = set(['userpass', 'root'])
    return list(given.difference(to_remove))


if __name__ == '__main__':
    client = vault_client()
    AVAILABLE_POLICIES = get_available_policies(client)
    users = get_formated_users()
    create_users(client, users)
