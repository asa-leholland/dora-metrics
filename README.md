# Start

1. Navigate to `https://github.com/settings/tokens`
2. Create an access token and save to GITHUB_PERSONAL_ACCESS_TOKEN in your `.env`
3. Create `github_config.csv` using the template to indicate which repos you want to analyze.
4. Create `failures.csv` using the template and populate with the failure results you want to analyze.
5. Create `usage.csv` using the template and populate with the usage data you want to analyze.
6. Setup environment using `python3 -m venv venv`.

## Test Suite

Open virtual env with `source venv/Scripts/activate`

Run `pytest --cov-report=xml --cov=main`

## Execution

To run, execute `python3 main.py`
