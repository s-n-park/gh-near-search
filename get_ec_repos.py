# Authentication is defined via github.Auth
import toml
import re
import os
import csv
from github import Auth, Github, Repository
import requests
import pandas as pd
from datetime import datetime,date
import time
import subprocess

# Load in from GH organizations
api_key = os.getenv('GITHUB_API_KEY')
headers = {'Authorization': f'token {api_key}'}

# update date
curr_date = str(date.today())

# Directory
directory = os.getenv('DIRECTORY_PATH')+'/crypto-ecosystems'
ec_directory = directory+'/crypto-ecosystems'

# Define Functions
def get_ec_repo(directory):
    if os.path.exists(directory):
        return # Already Downloaded Repo
    else:
        try:
            subprocess.run(["git", "clone", "https://github.com/electric-capital/crypto-ecosystems.git", directory], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")

# Fetch latest from GitHub
def pull_latest_from_github(repo_path):
    # Navigate to the repository directory and pull the latest changes
    try:
        subprocess.run(f"cd {repo_path} && git checkout master && git pull", check=True, shell=True)
    except subprocess.CalledProcessError as e:
        subprocess.run(f"cd {repo_path} && git stash && git checkout master && git pull origin master", check=True, shell=True)

# Define functions
def replace_name(name):
    name = re.sub(r'\W+', '-', name).lower()
    return name[:-1] if name.endswith('-') else name

def find_file(file,ec_directory):
    file = replace_name(file)+'.toml'
    foldername=file[0]
    for root, dirs, files in os.walk(ec_directory):
        if os.path.basename(root) == foldername:
            if file in files:
                return os.path.join(root, file)
    return None

def load_repos(repo_master,toml):
    for i in toml['repo']:
        repo_master.append(i['url'])
    return list(set(repo_master))

def load_subecosystems(sub_master,org_master,toml):
    for i in toml['sub_ecosystems']:
        sub_master.append(i)
    for i in toml['github_organizations']:
        org_master.append(i)
    return list(set(sub_master)),list(set(org_master))

def get_org_repos(org):
    org_name = org.split('/')[-1]
    api_request = f"https://api.github.com/orgs/{org_name}/repos"
    # print(api_request)
    req = requests.get(api_request,headers=headers)
    while req.status_code == 403:
        print("403 Error")
        time.sleep(60)
        req = requests.get(api_request)
    data = req.json()
#     time.sleep(1)
    return [r['html_url'] for r in data if 'html_url' in r]

# for each sub-ecosystem, 1) load their file 2) note sub-ecosystems, 3) add repos, 4) Add organizations
def process_sub_ecosystem(sub_ecosystem,near_repos_master,sub_ecosystems_master,org_master):
    filepath = find_file(sub_ecosystem,f'{ec_directory}/data/ecosystems')
    # 1. Load toml file
    toml_data = toml.load(filepath)
    # 2. Load subecosystems
    sub_ecosystems_master,org_master = load_subecosystems(sub_ecosystems_master,org_master,toml_data)
    # 3. Load Repos
    near_repos_master = load_repos(near_repos_master,toml_data)
    
    near_repos_master.sort()
    
    return near_repos_master,sub_ecosystems_master,org_master

# Load the repos from org master into repo_master
def load_organization_repos(repo_master,org_master):
    for i in org_master:
        repo_master.extend(get_org_repos(i))
    return list(set(repo_master))

def main():
    # Check if EC Loaded
    get_ec_repo(directory)
    
    # Load in latest from EC File
    pull_latest_from_github(ec_directory)
    
    # Load the near toml file
    near_toml_path = ec_directory+'/data/ecosystems/n/near.toml'
    near_toml = toml.load(near_toml_path)

    # first load NEAR Repos
    near_repos_master = []
    sub_ecosystems_master = []
    org_master = []
    near_repos_master = load_repos(near_repos_master,near_toml)
    sub_ecosystems_master,org_master = load_subecosystems(sub_ecosystems_master,org_master,near_toml)

    # Loop through sub-ecosystems
    change = 1

    while change != 0:
        prev_repos = len(near_repos_master)

        for sub in sub_ecosystems_master:
            near_repos_master,sub_ecosystems_master,org_master = process_sub_ecosystem(sub,near_repos_master,sub_ecosystems_master,org_master)

        change = len(near_repos_master) - prev_repos 
        print(f"Added {change} to repo master")

    # Load repos into near_repos_master
    near_repos_master = load_organization_repos(near_repos_master,org_master)

    # Sort the repos
    near_repos_master.sort()

    # Save as toml file
    data = {"repo":near_repos_master}

    with open(f'{directory}/all_near_repos_{curr_date}.toml','w') as toml_file:
        toml.dump(data,toml_file)

    # Save as csv file
    with open(f'{directory}/all_near_repos_{curr_date}.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for repo in near_repos_master:
            url = repo.split('.com/')[1]
            writer.writerow([url])

    print(f"Saved {len(near_repos_master)} NEAR repositories to all_near_repos_{curr_date}.csv")

if __name__ == "__main__":
    main()