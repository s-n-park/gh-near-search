import requests
import csv
import time
from datetime import datetime,timedelta, date
import os

# GitHub API URL for searching repositories
repo_url = "https://api.github.com/search/repositories"
code_url = "https://api.github.com/search/code"

# GH API Key
api_key = os.getenv('GITHUB_API_KEY')
headers = {'Authorization': f'token {api_key}'}

# Directory
directory = os.getcwd()

# Set this for timeframe we want to search over
last_x_days = 30

# Get Current date
curr_date = str(date.today())
min_date = (datetime.now() - timedelta(days=last_x_days)).strftime('%Y-%m-%d')

# Flatten the list if it's a list of lists
def flatten_list(lst):
    if lst and isinstance(lst[0], list):
        return [item for sublist in lst for item in sublist]

# Load list of tracked EC repos:
def load_ec_tracked_repos(curr_date):
    with open(f'{directory}/all_near_repos_{curr_date}.csv', 'r') as f:
        reader = csv.reader(f)
        repos = list(reader)
    ec_tracked_repos = flatten_list(repos)
    return set(ec_tracked_repos)

# Load list of previously audited repos that are not NEAR related
# This list will grow over time and is meant to prevent multiple manual review of the same repo
def load_reviewed_repos_to_exclude():
    with open('{directory}/checked_repos_to_exclude.csv', 'r') as f:
        reader = csv.reader(f)
        repos = list(reader)
    checked_repos = flatten_list(repos)
    return set(checked_repos)

# Check if the repo is included in the new_repos list
def check_if_repo_loaded(repo,loaded_repos,checked_repos,new_repos,type):
    # Determine repo_name based on type
    repo_name = repo['full_name'] if type == "repo" else repo['repository']['full_name']

    # Check if the repository is not in the 1) EC list, 2) manually reviewed list, and 3) new repos
    if repo_name not in loaded_repos and repo_name not in checked_repos and repo_name not in new_repos:
        new_repos.append(repo_name)

# Check and load repos
def check_and_load_repos(data, loaded_repos, checked_repos,new_repos,type):
    for repo in data['items']:
        check_if_repo_loaded(repo, loaded_repos, checked_repos,new_repos,type)

# Make a request to the GitHub API
def make_request(url, parameters, headers):
    response = requests.get(url, params=parameters, headers=headers)
    if response.status_code == 200:
        return response
    else:
        try:
            response = requests.get(url, params=parameters, headers=headers)
        except Exception as e:
            return e

def search_repos():
    # Load the list of repositories from the CSV file
    ec_tracked_repos = load_ec_tracked_repos(curr_date)

    # Load the list of already checked repositories from another CSV file
    checked_repos = load_reviewed_repos_to_exclude()

    # Initialize an empty list for new repositories to review
    new_repos = []

    # Search queries as list of dictionaries
    queries = [
        {"type":"repo","query":"\"near-api-js\""},
        {"type":"repo","query":"near-wallet -owner:near"},
        {"type":"repo","query":"near lake -owner:near"},
        {"type":"repo","query":"near indexer -owner:near"},
        {"type":"repo","query":"near rpc -owner:near"},
        {"type":"repo","query":"content:README.md near protocol -owner:near"},
        {"type":"repo","query":"\"near-sdk\" stars:1..150"},
        {"type":"repo","query":"\"near-cli\" stars:1..150"},
        {"type":"repo","query":"\"py-near\" -owner:near"},
        {"type":"code","query":"py-near -owner:near"},
        {"type":"code","query":"near-sdk -owner:near"},
        {"type":"code","query":"near-api-js -owner:near"},
    ]

    for q in queries:
        # Set the URL based on the type of query
        if q["type"] == "repo":
            url = "https://api.github.com/search/repositories"
            push = f" pushed:>{min_date}" # Only repos support pushed date
            per_page=100
        elif q["type"] == "code":
            url = "https://api.github.com/search/code"
            push = ""
            per_page=1000
        
        # Loop through pages
        page_num = 1
        while True:
            parameters = {"q": f"{q['query']}{push}", "page": page_num, "per_page": per_page}
            print(parameters)
            response = make_request(url, parameters, headers)
            data = response.json()
            check_and_load_repos(data, ec_tracked_repos, checked_repos, new_repos, q["type"])
            if q["type"] == "code":
                time.sleep(6) # rate limits to 10 requests per minute
            if 'next' in response.links:
                page_num += 1
                print(page_num)
            else:
                break

    # Dedupe new repos
    new_repos = list(set(new_repos))

    # Write new repos to a CSV file
    with open(f'{directory}/new_repos_{curr_date}.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        for repo in new_repos:
            writer.writerow([repo])

# Manually review the list of repos in new_repos
# For those repos that are not NEAR related, add them to checked_repos_to_exclude.csv
# For those repos that are NEAR related, add them near.toml in PR
# Any repos identified as organizations should also be added