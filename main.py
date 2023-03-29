import csv
import json
import os
import subprocess
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

import pandas as pd

with open('.env', 'r') as file:
    for line in file:
        if line.strip() and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

GITHUB_PERSONAL_ACCESS_TOKEN = os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')



def read_github_config(file_path) -> dict:
    config = {}
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            app_name = row['application_name']
            owner= row['github_owner']
            repo = row['github_repo']
            branch = row['main_branch']
            if app_name and repo and branch:
                config[app_name] = {'repo': repo, 'branch': branch, 'owner': owner}
    return config


def read_failure_csv(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df['datetime_failure_reported'] = pd.to_datetime(df['datetime_failure_reported'])
    df['datetime_failure_remedied'] = pd.to_datetime(df['datetime_failure_remedied'])
    return df


def read_usage_csv(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    return df


# def get_deployment_frequency(github_config, github_personal_access_token):
#     deployment_frequency = {}
#     g = Github(github_personal_access_token)
#     for app_name, config in github_config.items():
#         repo = g.get_repo(config['repo'])
#         branch = config['branch']
#         commits = repo.get_commits(sha=branch, since=datetime.now() - pd.Timedelta(weeks=1))
#         deployment_frequency[app_name] = commits.totalCount
#     return deployment_frequency



def use_github_cli_to_calculate_lead_time(owner, repo, branch) -> dict:

    time_period_days = 7

    def run_gh_command(command):
        result = subprocess.run(command, stdout=subprocess.PIPE, shell=True)
        return result.stdout.decode('utf-8')

    since_date = (datetime.now() - timedelta(days=time_period_days)).strftime('%Y-%m-%dT%H:%M:%SZ')
    pulls_command = f'gh api repos/{owner}/{repo}/pulls?state=closed'
    pulls_output = run_gh_command(pulls_command)
    pulls = json.loads(pulls_output)
    filtered_pulls = []
    for pull in pulls:
        if pull['merged_at'] is not None and pull['merged_at'] > since_date and pull['base']['ref'] == branch:
            filtered_pulls.append(pull)

    lead_times = []
    for pull in filtered_pulls:
        if pull['merged_at'] is not None:
            merge_date = datetime.strptime(pull['merged_at'], '%Y-%m-%dT%H:%M:%SZ')
            commits_url = pull['commits_url']
            commits_command = f'gh api {commits_url}'
            commits_output = run_gh_command(commits_command)
            commits = json.loads(commits_output)
            for commit in commits:
                commit_date = datetime.strptime(commit['commit']['author']['date'], '%Y-%m-%dT%H:%M:%SZ')
                lead_time = calculate_business_minutes(commit_date, merge_date) * 60
                lead_times.append(lead_time)

    if lead_times:
        average_lead_time = sum(lead_times) / len(lead_times)
        print(f'Average lead time for {repo}: {average_lead_time:.2f} seconds ({len(lead_times)} deployments))')
        return {'average_lead_time': average_lead_time, 'sum': sum(lead_times), 'count': len(lead_times)}
    else:
        print(f' - No lead times found for {repo}.')
        return {'average_lead_time': 0, 'sum': 0, 'count': 0}

def write_github_data_to_csv(github_data):
    github_data = read_github_config('github_config.csv')
    with open('github_data.csv', 'w') as f:
        f.write('app_name,average_lead_time_seconds,deployment_count\n')
    for app_name, config in github_data.items():
        owner = config['owner']
        repo = config['repo']
        branch = config['branch']
        result = use_github_cli_to_calculate_lead_time(owner, repo, branch)
        with open('github_data.csv', 'a') as f:
            f.write(f'{app_name},{result["average_lead_time"]},{result["count"]}\n')



def get_lead_time_for_changes_in_seconds_per_app(github_data: dict) -> dict:
    lead_time_for_changes = {}
    for app_name, commits in github_data.items():
        lead_times = []
        for commit in commits:
            if commit['merged']:
                lead_time = commit['merged_at'] - commit['created_at']
                lead_times.append(lead_time.total_seconds())
        if lead_times:
            avg_lead_time = sum(lead_times) / len(lead_times)
            lead_time_for_changes[app_name] = avg_lead_time
        else:
            lead_time_for_changes[app_name] = 0
    return lead_time_for_changes


def get_change_failure_rate(failure_df, deployment_frequency):
    change_failure_rate = {}
    for app_name, freq in deployment_frequency.items():
        app_failures = failure_df[failure_df['application_name'] == app_name]
        if freq > 0:
            change_failure_rate[app_name] = len(app_failures) / freq
        else:
            change_failure_rate[app_name] = 0
    return change_failure_rate


def get_time_to_restore_service(failure_df):
    time_to_restore_service = {}
    for app_name in failure_df['application_name'].unique():
        app_failures = failure_df[failure_df['application_name'] == app_name]
        time_to_restore_list = []
        for _, row in app_failures.iterrows():
            time_to_restore_list.append((row['datetime_failure_remedied'] - row['datetime_failure_reported']).total_seconds())
        if time_to_restore_list:
            avg_time_to_restore_service = sum(time_to_restore_list) / len(time_to_restore_list)
            time_to_restore_service[app_name] = avg_time_to_restore_service
        else:
            time_to_restore_service[app_name] = 0
    return time_to_restore_service


def write_metrics_to_csv(deployment_frequency, lead_time_for_changes, change_failure_rate, time_to_restore_service, file_path):
    with open(file_path, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['application_name', 'deployment_frequency', 'lead_time_for_changes', 'change_failure_rate', 'time_to_restore_service', 'user_usage', 'api_usage'])
        for app_name in deployment_frequency.keys():
            writer.writerow([app_name,
                             deployment_frequency.get(app_name, 0),
                             lead_time_for_changes.get(app_name, 0),
                             change_failure_rate.get(app_name, 0),
                             time_to_restore_service.get(app_name, 0)])


def read_failure_csv(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df['datetime_failure_reported'] = pd.to_datetime(df['datetime_failure_reported'])
    df['datetime_failure_remedied'] = pd.to_datetime(df['datetime_failure_remedied'])
    return df

def calculate_business_minutes(start_time, end_time):
        # Calculate the number of business minutes between two datetimes
        business_minutes = 0
        current_time = start_time
        while current_time < end_time:
            if current_time.weekday() < 5 and current_time.hour >= 6 and current_time.hour < 22:
                business_minutes += 1
            current_time += pd.Timedelta(minutes=1)
        return business_minutes

def calculate_failure_metrics(df: pd.DataFrame) -> pd.DataFrame:


    # Calculate the time to restore service for each failure
    df['time_to_restore_service'] = df.apply(lambda row: calculate_business_minutes(row['datetime_failure_reported'], row['datetime_failure_remedied']), axis=1)

    # Group the data by app name
    grouped = df.groupby('app_name')

    # Calculate the number of failures and average time to restore service for each app
    metrics = grouped.agg(
        number_of_failures=('app_name', 'count'),
        average_time_to_restore_service_minutes=('time_to_restore_service', 'mean')
    ).reset_index()

    # calculate the median time to restore service for each app
    metrics = metrics.merge(
        grouped.agg(
            median_time_to_restore_service_minutes=('time_to_restore_service', 'median')
        ).reset_index(),
        on='app_name'
    )

    return metrics

def main(github_config_file_path,
         failure_excel_file_path,
         usage_excel_file_path,
         output_csv_file_path):



    # github_config = read_github_config(github_config_file_path)

    # write_github_data_to_csv(github_config)

    with open('github_data.csv', 'r') as f:
        lead_time_df = pd.read_csv(f)

        failure_df = read_failure_csv(failure_excel_file_path)
        metrics = calculate_failure_metrics(failure_df)

        # combine the two dataframes
        result = pd.merge(lead_time_df, metrics, how='left', left_on='app_name', right_on='app_name')
        # convert all NaN values to 0
        result = result.fillna(0)
        # for all cells containing a float, round to nearest integer
        result['average_lead_time_business_days'] = result['average_lead_time_seconds'] / 60 / 60 / 8

        result['average_lead_time_business_days'] = result['average_lead_time_business_days'].round(1)
        result['average_lead_time_business_days'] = result['average_lead_time_business_days'].round(0)

        # drop the average_lead_time_seconds column
        result = result.drop(columns=['average_lead_time_seconds', 'average_time_to_restore_service_minutes'])

        # add a column that calculates the percentage of failures over the number of deployments for each app (if there are no deployments, the percentage is 0)
        result = result.assign(change_failure_rate=lambda x: x['number_of_failures'] / x['deployment_count'] * 100)

        # correct for any NaN values and inf values
        result = result.fillna(0)
        result = result.replace([np.inf, -np.inf], 0)

        result = result.drop(columns=['number_of_failures'])

        # loop over all rows in the dataframe
        # loop over all columns
            # for each cell, if it is a float, round to nearest integer


        # add an additional column for the number of average lead time in days
        print(result)
        result.to_csv('output.csv', index=False)



    # write_metrics_to_csv(deployment_frequency,
    #                      lead_time_for_changes,
    #                      change_failure_rate,
    #                      time_to_restore_service,
    #                      output_csv_file_path)


if __name__ == '__main__':
    main('github_config.csv',
         'failures.csv',
         'usage.csv',
         'output.csv',)
