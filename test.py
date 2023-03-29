import os
from datetime import datetime
from io import StringIO

import pandas as pd
from pandas.testing import assert_frame_equal

from main import (
                  read_failure_csv, read_github_config,
                   get_lead_time_for_changes_in_seconds_per_app)


from datetime import datetime

def test_get_lead_time_seconds_for_changes():
    # Create sample github_data
    github_data = {
        'app1': [
            {'merged': True,
             'merged_at': datetime(2022, 1, 1, 12, 0, 0),
             'created_at': datetime(2022, 1, 1, 10, 0, 0)},
            {'merged': True,
             'merged_at': datetime(2022, 1, 2, 12, 0, 0),
             'created_at': datetime(2022, 1, 2, 9, 0, 0)}
        ],
        'app2': [
            {'merged': True,
             'merged_at': datetime(2022, 1, 3, 12, 0, 0),
             'created_at': datetime(2022, 1, 3, 10, 0, 0)},
        ],
    }

    result = get_lead_time_for_changes_in_seconds_per_app(github_data)

    assert result == {'app1': 9000.0, 'app2': 7200.0}

def test_read_github_config():
    MOCK_CONFIG_FILENAME = 'config.csv'
    config_file = StringIO("""application_name,github_owner,github_repo,main_branch
app1,user,repo1,master
app2,user,repo2,main
""")
    with open(MOCK_CONFIG_FILENAME, 'w') as file:
        file.write(config_file.read())

    config = read_github_config(MOCK_CONFIG_FILENAME)

    assert set(config.keys()) == {'app1', 'app2'}
    assert set(config['app1'].keys()) == {'owner', 'repo', 'branch'}
    assert set(config['app2'].keys()) == {'owner', 'repo', 'branch'}
    assert config['app1']['owner'] == 'user'
    assert config['app1']['repo'] == 'repo1'
    assert config['app1']['branch'] == 'master'
    assert config['app2']['owner'] == 'user'
    assert config['app2']['repo'] == 'repo2'
    assert config['app2']['branch'] == 'main'

    os.remove(MOCK_CONFIG_FILENAME)



def test_read_failure_csv(tmpdir):
    MOCK_CONFIG_FILENAME = 'mock_failures.csv'
    file_path = tmpdir.join(MOCK_CONFIG_FILENAME)
    data = {
        'application_name': ['app1', 'app2'],
        'datetime_failure_reported': ['2022-01-01 12:00:00', '2022-01-02 13:00:00'],
        'datetime_failure_remedied': ['2022-01-01 14:00:00', '2022-01-02 15:00:00']
    }
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)

    result = read_failure_csv(file_path)

    expected = pd.DataFrame({
        'application_name': ['app1', 'app2'],
        'datetime_failure_reported': [datetime(2022, 1, 1, 12, 0, 0), datetime(2022, 1, 2, 13, 0, 0)],
        'datetime_failure_remedied': [datetime(2022, 1, 1, 14, 0, 0), datetime(2022, 1, 2, 15, 0, 0)]
    })

    assert_frame_equal(result, expected)

    os.remove(file_path)
