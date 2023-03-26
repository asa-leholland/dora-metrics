import csv
from datetime import datetime
import pandas as pd
import os
from github import Github


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
            repo = row['github_repo']
            branch = row['main_branch']
            config[app_name] = {'repo': repo, 'branch': branch}
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


def get_github_data(github_config, github_token):
    github_data = {}
    g = Github(github_token)
    for app_name, config in github_config.items():
        repo = g.get_repo(config['repo'])
        branch = config['branch']
        pulls = repo.get_pulls(state='closed', base=branch)
        pull_data = []
        for pull in pulls:
            pull_data.append({
                'merged': pull.merged,
                'merged_at': pull.merged_at,
                'created_at': pull.created_at
            })
        github_data[app_name] = pull_data
    return github_data


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


def main(github_config_file_path,
         failure_excel_file_path,
         usage_excel_file_path,
         output_csv_file_path):

    github_config = read_github_config(github_config_file_path)

    failure_df = read_failure_csv(failure_excel_file_path)

    # usage_df = read_usage_csv(usage_excel_file_path)

    # deployment_frequency = get_deployment_frequency(github_config)

    lead_time_for_changes = get_lead_time_for_changes_in_seconds_per_app(github_config)

    # change_failure_rate = get_change_failure_rate(failure_df, deployment_frequency)

    time_to_restore_service = get_time_to_restore_service(failure_df)

    # write_metrics_to_csv(deployment_frequency,
    #                      lead_time_for_changes,
    #                      change_failure_rate,
    #                      time_to_restore_service,
    #                      output_csv_file_path)


if __name__ == '__main__':
    main('github_config.csv',
         'failure_excel.xlsx',
         'usage_excel.xlsx',
         'output.csv',)
