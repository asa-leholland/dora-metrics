# Start

1. Navigate to <https://github.com/settings/tokens>
2. Create an access token and save to GITHUB_PERSONAL_ACCESS_TOKEN in your `.env`
3. Install GitHub Cli using `brew install gh` on Mac or `winget installl --id GitHub.cli` on Windows.
4. Run `gh auth login` and provide GitHub credentials.
5. Create `github_config.csv` using the template to indicate which repos you want to analyze.
6. Create `failures.csv` using the template and populate with the failure results you want to analyze.
7. Create `usage.csv` using the template and populate with the usage data you want to analyze.
8. Setup environment using `python3 -m venv venv`.
9. Run `pip install -r requirements.txt`

## Test Suite

Open virtual env with `source venv/Scripts/activate` on Windows or `source venv/bin/activate` on Mac.

Run `pytest --cov-report=xml --cov=main`

## Execution

To run, execute `python3 main.py`
