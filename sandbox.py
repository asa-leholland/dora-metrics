from datetime import datetime
import csv
from datetime import datetime
# import pandas as pd
import pandas as pd
import requests
from io import StringIO

import requests
import json

import subprocess
import json
from datetime import datetime, timedelta

import os
from github import Github

GITHUB_PERSONAL_ACCESS_TOKEN = os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
GITHUB_OWNER = os.getenv('GITHUB_OWNER')


def get_github_data(token, owner, repo_name):

    r = requests.get(
        f'https://api.github.com/repos/{owner}/{repo_name}/commits',
        headers={
            'accept': 'application/vnd.github.v3+json',
            'authorization': f'token {token}',
        },
    )

    # parse response
    commit_data = json.loads(r.text)

    print(commit_data)

    # create CSV file
    with open('commit_data.csv', 'w') as f:
        f.write('sha,author,date,message\n')
        for commit in commit_data:
            sha = commit['sha']
            author = commit['commit']['author']['name']
            date = commit['commit']['author']['date']
            message = commit['commit']['message'].replace('\n', ' ')
            f.write(f'{sha},{author},{date},{message}\n')



def read_github_config(file_path) -> dict:
    config = {}
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            app_name = row['application_name']
            repo = row['github_repo']
            branch = row['main_branch']
            if app_name and repo and branch:
                config[app_name] = {'repo': repo, 'branch': branch}
    return config



def foo(owner, repo, branch):

    # Set the time period for calculating lead time for changes (in days)
    time_period = 7

    # Define a function to run a GitHub CLI command and return the output
    def run_gh_command(command):
        result = subprocess.run(command, stdout=subprocess.PIPE, shell=True)
        return result.stdout.decode('utf-8')


    # Get the pull requests that were merged into the specified branch within the specified time period
    since_date = (datetime.now() - timedelta(days=time_period)).strftime('%Y-%m-%dT%H:%M:%SZ')
    pulls_command = f'gh api repos/{owner}/{repo}/pulls?state=closed&sort=updated --paginate'
    pulls_output = run_gh_command(pulls_command)
    pulls = json.loads(pulls_output)
    filtered_pulls = []
    for pull in pulls:
        criteria = [
            pull['merged_at'] is not None,
            pull['merged_at'] > since_date,
            # pull['base'] == branch,


        ]
        if all(criteria):
            filtered_pulls.append(pull)
    print(filtered_pulls)

    # Calculate the lead time for changes
    lead_times = []
    for pull in pulls:
        if pull['merged_at']:
            merge_date = datetime.strptime(pull['merged_at'], '%Y-%m-%dT%H:%M:%SZ')
            commits_url = pull['commits_url']
            commits_command = f'gh api {commits_url} --paginate'
            commits_output = run_gh_command(commits_command)
            commits = json.loads(commits_output)
            for commit in commits:
                commit_date = datetime.strptime(commit['commit']['author']['date'], '%Y-%m-%dT%H:%M:%SZ')
                lead_time = (merge_date - commit_date).total_seconds()
                lead_times.append(lead_time)

    if lead_times:
        average_lead_time = sum(lead_times) / len(lead_times)
        print(f'Average lead time for changes: {average_lead_time:.2f} seconds')
    else:
        print('No lead times found')

github_data = read_github_config('github_config.csv')
print(github_data)

# for app_name, config in github_data.items():
#     repo_name = config['repo'].split('/')[1]
print(foo('asa-leholland', 'dora-metrics', 'main'))
    # print(get_github_data(GITHUB_PERSONAL_ACCESS_TOKEN, GITHUB_OWNER, repo_name))


