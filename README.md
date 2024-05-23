# GitHub Repo Search

## Project Description

This project aims to accomplish two main tasks:

1. Scrape Electric Capital repositories: The code will scrape the Electric Capital repo on GitHub and retrieve the full list of GitHub Repos from the near.toml file

2. Search for other GitHub repositories: The code will search for repositories on GitHub that are not included that list of GitHub repos using a variety of search queries.

## Installation/Setup

Instructions on how to install and set up your project:

1. Clone the repository:
    ```
    git clone https://github.com/your_username/your_project.git
    ```

2. Navigate to the project directory:
    ```
    cd your_project
    ```

3. Install the required dependencies:
    ```
    pip install -r requirements.txt
    ```

4. Set the environment variables:
    ```
    export GH_API_KEY=your_api_key
    export DIRECTORY=/path/to/directory
    ```

5. Run the project:
    ```
    python main.py
    ```

Please make sure you have Python and pip installed on your system before proceeding with the installation.

## Details
1. 
The Python script, get_ec_repos.py, fetches data from these near.toml, processes it, and saves the resulting list of all github repos in two formats: a TOML (Tom's Obvious, Minimal Language) file and a CSV (Comma Separated Values) file.

Here's a brief summary of the files saved:

TOML File: The script saves a TOML file named all_near_repos_{curr_date}.toml in the directory specified by the DIRECTORY_PATH environment variable. This file contains a list of NEAR repositories. Each repository is represented as a URL and they are all stored under the key repo.

CSV File: The script also saves a CSV file named all_near_repos_{curr_date}.csv in the same directory. This file contains the same list of NEAR repositories as the TOML file, but in a different format. Each line in the CSV file represents a repository, and the repository URL is split at '.com/' and only the part after '.com/' is saved.

The {curr_date} in the filenames is the current date, which is fetched using the date.today() function from the datetime module. This means that each time the script is run, it will generate new files for that specific date.

2. 
The search_github.py script is designed to search GitHub for repositories and code related to the NEAR protocol. It uses the GitHub API to perform these searches and processes the results to identify new repositories that may be of interest. It uses 3 lists to keep track of repositories:

1. Tracked EC Repositories: This list, ec_tracked_repos, is loaded from a CSV file named **all_near_repos_{curr_date}.csv**. It contains repositories that are already being tracked because they are related to the NEAR protocol. The script uses this list to avoid re-processing repositories that have already been identified as relevant.

2. Reviewed Repositories to Exclude: This list is loaded from a CSV file named **checked_repos_to_exclude.csv**. It contains repositories that have been manually reviewed and determined to be not related to the NEAR protocol. The script uses this list to avoid re-processing repositories that have already been identified as irrelevant.

3. new_repos, which starts as an empty list and is populated with repositories found by the search queries that are not in either of the other two lists. This list is saved to a CSV file named **new_repos_{curr_date}.csv** at the end of the script. These are the repositories that need to be manually reviewed to determine if they are related to the NEAR protocol.

Manual Review: We suggest that the user manually review the new repositories. Repositories that are not related to NEAR should be added to the list of reviewed repositories, and repositories that are related to NEAR should be added to a TOML file in a pull request.

After finishing manual review, add those lists to the file: **checked_repos_to_exclude.csv** so that they can be excluded in future runs
