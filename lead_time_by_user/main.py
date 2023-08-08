from datetime import datetime
import os

ACCESS_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

def calculate_average_commit_time(repo, branch, start_date, end_date):
    commits = repo.get_commits(sha=branch)
    user_commit_times = {}
    for commit in commits:
        commit_date = commit.commit.author.date
        merge_date = get_merge_date(repo, commit.sha)
        if merge_date and is_within_date_range(merge_date, start_date, end_date):
            time_to_production = merge_date - commit_date
            username = commit.author.login
            if username not in user_commit_times:
                user_commit_times[username] = []
            user_commit_times[username].append(time_to_production.total_seconds() / (3600 * 24))

    return user_commit_times

def get_merge_date(repo, sha):
    pull_requests = repo.get_pulls(state='closed', sort='updated', base=repo.default_branch)
    for pull_request in pull_requests:
        if pull_request.merged_at and sha in pull_request.merge_commit_sha:
            return pull_request.merged_at

    return None

def is_within_date_range(date, start_date, end_date):
    return start_date <= date <= end_date

import subprocess
import json
from datetime import datetime, timedelta

def use_github_cli_to_calculate_lead_time(owner, repo, branch, start_date: datetime, end_date: datetime) -> dict:


    def run_gh_command(command):
        result = subprocess.run(command, stdout=subprocess.PIPE, shell=True)
        return result.stdout.decode('utf-8')

    def calculate_lead_time_in_days(start_date, end_date) -> float:
        lead_time_in_days = (end_date - start_date).total_seconds() / (3600 * 24)
        return lead_time_in_days

    end_date_formatted = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    start_date_formatted = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')

    pulls_command = f'gh api repos/{owner}/{repo}/pulls?state=closed'
    pulls_output = run_gh_command(pulls_command)
    pulls = json.loads(pulls_output)


    user_lead_times = {}

    for pull in pulls:
        if pull['merged_at'] is not None and pull['merged_at'] > start_date_formatted and pull['merged_at'] < end_date_formatted and pull['base']['ref'] == branch:
            merge_date = datetime.strptime(pull['merged_at'], '%Y-%m-%dT%H:%M:%SZ')
            commits_url = pull['commits_url']
            commits_command = f'gh api {commits_url}'
            commits_output = run_gh_command(commits_command)
            commits = json.loads(commits_output)
            for commit in commits:
                commit_date = datetime.strptime(commit['commit']['author']['date'], '%Y-%m-%dT%H:%M:%SZ')
                lead_time = calculate_lead_time_in_days(commit_date, merge_date)
                user = commit['author']['login']  if commit['author'] else 'unknown'
                if user not in user_lead_times:
                    user_lead_times[user] = []
                user_lead_times[user].append(lead_time)

    if user_lead_times:
        user_stats = {}
        for user, lead_times in user_lead_times.items():
            average_lead_time = sum(lead_times) / len(lead_times)

            pull_count = 0
            for pull in pulls:
                if pull['merged_at'] is not None and pull['merged_at'] > start_date_formatted and pull['merged_at'] < end_date_formatted and pull['base']['ref'] == branch and pull['user']['login'] == user:
                    pull_count += 1
            user_stats[user] = {'average_lead_time': average_lead_time, 'count': pull_count}
        return user_stats
    else:
        return {}


def main():
    repositories = [
        {"application_name": "SFS Testcard", "github_owner": "fluxergy", "github_repo": "mos-sfs", "main_branch": "develop"},
        {"application_name": "FPKG", "github_owner": "fluxergy", "github_repo": "mos-fpkg", "main_branch": "main"},
        {"application_name": "TPS", "github_owner": "fluxergy", "github_repo": "mos-tps", "main_branch": "main"},
        {"application_name": "IMS API", "github_owner": "fluxergy", "github_repo": "mos-ims-api", "main_branch": "main"},
        {"application_name": "IMS UI", "github_owner": "fluxergy", "github_repo": "mos-ims-react", "main_branch": "main"},
        {"application_name": "Admin", "github_owner": "fluxergy", "github_repo": "mos-admin", "main_branch": "main"},
        {"application_name": "BOM API", "github_owner": "fluxergy", "github_repo": "mos-api", "main_branch": "main"},
        {"application_name": "SFS Device UI", "github_owner": "fluxergy", "github_repo": "mos-sfs-react", "main_branch": "develop"},
        {"application_name": "SFS Device API", "github_owner": "fluxergy", "github_repo": "mos-sfs-device-api", "main_branch": "develop"},
    ]

    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 6, 30)


    print("| repository | username | average time to get commit into production (days) | number of merges |")
    print("|------------|----------|-----------------------------------------------| ------------------|")

    for repo_data in repositories:
        owner = repo_data["github_owner"]
        repo_name = repo_data["github_repo"]
        branch = repo_data["main_branch"]
        application_name = repo_data["application_name"]

        user_commit_times = use_github_cli_to_calculate_lead_time(owner, repo_name, branch, start_date, end_date)

        for username, commit_times in user_commit_times.items():
            average_time = commit_times["average_lead_time"]
            print(f"| {application_name} | {username} | {average_time:.2f} | {commit_times['count']} |")

if __name__ == "__main__":
    main()
