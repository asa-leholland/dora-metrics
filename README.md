# DORA Metrics

This project is a data analysis and reporting tool for tracking software development and deployment metrics. The purpose of this project is to gather data from various sources, process it, and generate meaningful metrics that provide insights into the efficiency, reliability, and quality of the software development process. The project includes the following main components:

Reading Configuration and Environment Variables:
The project starts by reading configuration data from a CSV file (github_config.csv) that contains information about different applications, their GitHub repositories, and associated settings. It also reads environment variables from a file (.env) to set up authentication tokens.

GitHub Data Retrieval:
The project retrieves data from GitHub repositories using the GitHub CLI (gh) and the GitHub API. It calculates the average lead time for changes in the repositories. Lead time is the time taken from the creation of a pull request to its successful merge. It calculates this metric based on the data from the past week and stores it in a CSV file (github_data.csv).

Failure Data Processing:
The project reads failure data from a CSV file (failures.csv) and processes it to calculate metrics related to failure analysis. It calculates the time it takes to restore service after a failure, groups failures by application, and calculates the average time to restore service for each application. These metrics are used to analyze the reliability of different applications.

Metrics Calculation:
The project calculates several metrics for each application, including deployment frequency, median time to restore service, average lead time (in business days), and change failure rate. These metrics provide insights into the development and deployment process, as well as the stability of the applications.

Data Integration and Transformation:
The project integrates the data from GitHub (lead time metrics) and failure analysis to create a unified dataset. It fills in missing or NaN values, calculates additional metrics like change failure rate, and rounds numerical metrics to appropriate units. The processed data is then transformed into a format suitable for reporting.

CSV Output:
Finally, the project writes the calculated metrics and analysis results to an output CSV file (output.csv) in a well-organized and readable format. This file serves as a report that stakeholders can use to gain insights into various aspects of the software development process.

Execution:
The main function of the script (main) orchestrates the entire process by calling the appropriate functions and passing the required file paths. The script can be executed from the command line, and it processes data from the provided input files (github_config.csv, failures.csv, usage.csv) to generate the final output file (output.csv).

Overall, this project aims to provide actionable insights into software development and deployment practices by analyzing GitHub data and failure reports, and then presenting the results in a structured and informative manner. It facilitates data-driven decision-making and helps improve the software development process by identifying areas of improvement and potential bottlenecks.

## Usage

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
