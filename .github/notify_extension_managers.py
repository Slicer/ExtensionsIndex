import os
import pandas as pd
import re
import requests
import logging
import time
from github import Github
import json

# Get the GitHub token from the environment variable
access_token = os.environ.get('GITHUB_TOKEN')

g = Github(access_token)
repo = g.get_repo("vkt1414/ExtensionsIndex")

# Define the target extension name
slicerExtensionName = 'IDCBrowser'

# API data retrieval and processing
api_url = f"https://slicer.cdash.org/api/v1/index.php?project=SlicerPreview"
response = requests.get(api_url)

if response.status_code == 200:
    api_result = response.json()
    api_call_time = api_result["datetime"]
    build_groups = api_result["buildgroups"]

    api_data = []
    for item in build_groups:
        builds = item['builds']
        for build in builds:
            build_data = {
                "id": item["id"],
                "name": item["name"],
                "label": build["label"],
                "APICallTime": api_call_time,
                "BuildTriggerTime": build["builddate"],
                "BuildName": build["buildname"],
                "BuildPlatform": build.get("buildplatform", None),
                "ConfigureErrors": build.get("configure", {}).get("error", 0),
                "ConfigureWarnings": build.get("configure", {}).get("warning", 0),
                "HasCompilationData": build.get("hascompilation", False),
                "CompilationErrors": build.get("compilation", {}).get("error", 0),
                "CompilationWarnings": build.get("compilation", {}).get("warning", 0),
                "HasTestData": build.get("hastest", False),
                "TestNotRun": build.get("test", {}).get("notrun", 0),
                "TestFail": build.get("test", {}).get("fail", 0),
                "TestPass": build.get("test", {}).get("pass", 0),
            }
            api_data.append(build_data)

    api_df = pd.DataFrame(api_data)
    api_df['ErrorSum'] = api_df['ConfigureErrors'] + api_df['CompilationErrors'] + api_df['TestFail']
    api_df['WarningSum'] = api_df['ConfigureWarnings'] + api_df['CompilationWarnings']
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")

# Process the CODEOWNERS file
# url = "https://raw.githubusercontent.com/vkt1414/ExtensionsIndex/main/CODEOWNERS"
# response = requests.get(url)
# lines = [line for line in response.text.split('\n') if line]
# Read the existing CODEOWNERS file
with open('CODEOWNERS', 'r') as file:
    existing_codeowners = [line.strip() for line in file if line.strip()]

# Read the NEW_CODEOWNERS file
with open('NEW_CODEOWNERS', 'r') as file:
    new_codeowners = [line.strip() for line in file if line.strip()]

# Extract existing extensions from the CODEOWNERS file
existing_extensions = [line.split(' ')[0] for line in existing_codeowners]

# Find new extensions present in NEW_CODEOWNERS but not in CODEOWNERS
new_extensions = [line for line in new_codeowners if line.split(' ')[0] not in existing_extensions]

# Append only the new extensions to the existing CODEOWNERS file
with open('CODEOWNERS', 'a') as file:
    for line in new_extensions:
        file.write(line + '\n')

# Read the file
with open('CODEOWNERS', 'r') as file:
    lines = [line.strip() for line in file if line.strip()]

data = []

pattern = r"/(.*)\.s4ext @(.*)"

for line in lines:
    match = re.search(pattern, line)
    if match:
        extension_name = match.group(1)
        poc = match.group(2)
        data.append([extension_name, poc])

codeowners_df = pd.DataFrame(data, columns=['ExtensionName', 'POC'])
merged_api_codeowners_df = api_df.merge(codeowners_df, left_on='label', right_on='ExtensionName', how='left').reset_index(drop=True).sort_values(by='label')

# Pivot the columns for data aggregation
columns_to_pivot = [
    'BuildName', 'ConfigureErrors', 'ConfigureWarnings', 'HasCompilationData',
    'CompilationErrors', 'CompilationWarnings', 'HasTestData', 'TestNotRun',
    'TestFail', 'TestPass', 'ErrorSum', 'WarningSum'
]

for column in columns_to_pivot:
    pivot = merged_api_codeowners_df.pivot_table(values=column, index='ExtensionName', columns='BuildPlatform', aggfunc='first', fill_value='Null')
    pivot.columns = [f'{col}_{column}' for col in pivot.columns]
    merged_api_codeowners_df = pd.merge(merged_api_codeowners_df, pivot, on='ExtensionName')

# Final data cleaning and compilation summary
merged_api_codeowners_df = merged_api_codeowners_df.drop(columns=columns_to_pivot + ['BuildPlatform'])
merged_api_codeowners_df = merged_api_codeowners_df.drop_duplicates(subset='ExtensionName')
merged_api_codeowners_df = merged_api_codeowners_df.reset_index(drop=True)

error_columns_df = merged_api_codeowners_df[['windows_ErrorSum', 'linux_ErrorSum', 'mac_ErrorSum']].apply(pd.to_numeric, errors='coerce')
warning_columns_df = merged_api_codeowners_df[['windows_WarningSum', 'linux_WarningSum', 'mac_WarningSum']].apply(pd.to_numeric, errors='coerce')

merged_api_codeowners_df['TotalErrors'] = error_columns_df.sum(axis=1)
merged_api_codeowners_df['TotalWarnings'] = warning_columns_df.sum(axis=1)

# Create JSON output for extensions with issues
extensions_with_issues_df = merged_api_codeowners_df[(merged_api_codeowners_df['TotalErrors'] > 0) | (merged_api_codeowners_df['TotalWarnings'] > 0)]
json_list = []

for index, row in extensions_with_issues_df.iterrows():
    extension_name = row['ExtensionName']
    header = f"{row['name']} {row['ExtensionName']}"
    poc = row['POC']
    errors = row['TotalErrors']
    warnings = row['TotalWarnings']

    issue_body = f"Hi {poc},\n\nDuring today's build of your extension, I found {errors} error(s) and {warnings} warning(s).\n\nHere's the breakdown by your extension's target platform:\n\n"

    platforms = ['linux', 'mac', 'windows']

    for platform in platforms:
        platform_build = row[f"{platform}_BuildName"]
        platform_errors = row[f"{platform}_ErrorSum"]
        platform_warnings = row[f"{platform}_WarningSum"]

        if platform_errors > 0 or platform_warnings > 0:
            issue_body += f"- {platform} ({platform_build}):\n"
            categories = {
                'Configure': f"{platform}_ConfigureErrors",
                'ConfigureWarnings': f"{platform}_ConfigureWarnings",
                'Compilation': f"{platform}_CompilationErrors",
                'CompilationWarnings': f"{platform}_CompilationWarnings",
                'TestFail': f"{platform}_TestFail"
            }

            for category, col in categories.items():
                category_errors = row[col]
                if category_errors > 0:
                    issue_body += f"  - {category}: {category_errors}"
                    if category == 'Configure' and row.get(f"{platform}_ConfigureWarnings"):
                        issue_body += f", Warnings({row[f'{platform}_ConfigureWarnings']})"
                    if category == 'Compilation' and row.get(f"{platform}_CompilationWarnings"):
                        issue_body += f", Warnings({row[f'{platform}_CompilationWarnings']})"
                    if category == 'TestFail' and row.get(f"{platform}_TestWarnings"):
                        issue_body += f", Warnings({row[f'{platform}_TestWarnings']})"
                    issue_body += '\n'

    issue = {
        "extension_name": extension_name,
        "poc": poc,
        "issue_header": header,
        "issue_body": issue_body
    }
    json_list.append(issue)

json_output = json.dumps(json_list, indent=2)

# # Parse the JSON output
issues = json.loads(json_output)

extensions_with_issues_list = [issue['extension_name'] for issue in issues]

existing_issues = repo.get_issues(state="open")  # Fetch all open issues

for index, row in merged_api_codeowners_df.iterrows():
    header = f"{row['name']} {row['ExtensionName']}"
    extension_name = row['ExtensionName']
    # Check if the issue title matches the pattern and is not in the list
    for issue in existing_issues:
        if header in issue.title and extension_name not in extensions_with_issues_list:
            print(f'Closing issue for {extension_name}')
            # Add a comment
            issue.create_comment("No errors or warnings found anymore, so closing this issue.")
            # Close the issue
            issue.edit(state='closed')


for issue in issues:
    header = issue['issue_header']
    body = issue['issue_body']
    extension_name = issue['extension_name']

    existing_issue = None
    for existing in existing_issues:
        if existing.title == header:  
            existing_issue = existing
            break
    
    if existing_issue is None:  
        while True:
            try:
                new_issue = repo.create_issue(title=header, body=body)
                print(f"Issue created for {extension_name} - {new_issue.html_url}")
                time.sleep(30)  
                break
            except Exception as e:
                print(header)
                print(body)
                print(f"Failed to create issue: {e}")
                time.sleep(30)
