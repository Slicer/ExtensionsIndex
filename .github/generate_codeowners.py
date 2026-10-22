import os
import pandas as pd
import re
import requests
import logging
import time
from github import Github
import json

# Set display options
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)

# Configure the logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def authenticate_github_session():
    """
    Authenticate a GitHub session using a personal access token.

    Returns:
        A requests.Session object configured with the necessary headers.
    """
    gh_session = requests.Session()

    if 'GITHUB_TOKEN' in os.environ:
        # Use the inbuilt GITHUB_TOKEN for authentication
        gh_session.headers.update({'Authorization': f'token {os.environ["GITHUB_TOKEN"]}'})
    else:
        # Use your personal token for authentication
        #gh_session.headers.update({'Authorization': f'token {github_token}'})
        os.exit(1)
    return gh_session

def get_repository_files(gh_session):
    """
    Retrieve the list of files in a GitHub repository.

    Args:
        gh_session (requests.Session): A GitHub session.

    Returns:
        list: A list of file metadata.
    """
    url = "https://api.github.com/repos/Slicer/ExtensionsIndex/contents"
    while True:
        response = gh_session.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error("Failed to get repository files. Retrying in 5 minutes...")
            time.sleep(300)

def get_contributors(gh_session, github_repo_api):
    """
    Get contributors for a GitHub repository.

    Args:
        gh_session (requests.Session): A GitHub session.
        github_repo_api (str): API URL of the GitHub repository.

    Returns:
        list: A list of contributors.
    """
    contributors_url = f"{github_repo_api}/contributors"
    while True:
        response = gh_session.get(contributors_url)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Failed to get contributors for {github_repo_api}. Retrying in 5 minutes...")
            time.sleep(300)

def get_pull_requests(gh_session, github_repo_api):
    """
    Get closed pull requests for a GitHub repository.

    Args:
        gh_session (requests.Session): A GitHub session.
        github_repo_api (str): API URL of the GitHub repository.

    Returns:
        list: A list of closed pull requests.
    """
    pull_requests_url = f"{github_repo_api}/pulls?state=closed"
    while True:
        response = gh_session.get(pull_requests_url)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Failed to get pull requests for {github_repo_api}. Retrying in 5 minutes...")
            time.sleep(300)

def get_commit(gh_session, commit_url):
    """
    Get commit data from a GitHub commit URL.

    Args:
        gh_session (requests.Session): A GitHub session.
        commit_url (str): URL of the GitHub commit.

    Returns:
        dict: Commit data.
    """
    while True:
        response = gh_session.get(commit_url)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Failed to get commit data from {commit_url}. Status code: {response.status_code}. Retrying in 5 minutes...")
            time.sleep(300)

def determine_point_of_contact(gh_session, extension_name, extension_file_content):
    """
    Determine the point of contact (POC) for a GitHub extension file.

    Args:
        gh_session (requests.Session): A GitHub session.
        extension_name (str): Name of the extension.
        extension_file_content (str): Content of the extension file.

    Returns:
        str: The point of contact (GitHub username) or None if not found.
    """
    point_of_contact = None
    # Find the scmurl line
    scmurl_line = re.search(r'^scmurl.*$', extension_file_content, re.MULTILINE)

    if scmurl_line is not None:
        # Get the GitHub repo URL
        github_repo = scmurl_line.group().split(' ')[1]

        # Replace github.com with api.github.com/repos in the URL
        github_repo_api = github_repo.replace('github.com', 'api.github.com/repos')

        # Remove .git from the end of the URL if it's present
        if github_repo_api.endswith('.git'):
            github_repo_api = github_repo_api[:-4]

        # Check if it's not another repository
        if "github.com" in github_repo:
            contributors = get_contributors(gh_session, github_repo_api)
            pull_requests = get_pull_requests(gh_session, github_repo_api)

            # Check if there is only one contributor
            if len(contributors) == 1 or len(pull_requests) == 0:
                point_of_contact = contributors[0]['login']
                logging.info("Found number of contributors: " + str(len(contributors)))
                logging.info("Point of contact: " + point_of_contact)
            else:
                # Find the closed pull requests for the repository
                if pull_requests:
                    # Find the latest closed pull request
                    latest_pull_request = pull_requests[0]
                    latest_pull_request_number = latest_pull_request['number']
                    if latest_pull_request['merge_commit_sha'] is not None:
                        merge_commit_sha = latest_pull_request['merge_commit_sha']

                        # Get the merge commit for the latest closed pull request
                        commit_url = f"{github_repo_api}/commits/{merge_commit_sha}"
                        commit = get_commit(gh_session, commit_url)
                        committer = commit['committer']['login']
                        if commit['committer']['login'] == 'web-flow':
                            if commit['author'] is not None:
                                committer = commit['author']['login']
                            else:
                                committer = None
                        point_of_contact = committer
                        logging.info("Found more than one contributor, so determining point of contact by whoever accepted the latest pull request \n")
                        if point_of_contact is not None:
                            logging.info("Point of contact: " + point_of_contact)
                        else:
                            logging.info("Point of contact is not available.")

    return point_of_contact

def process_extensions():
    """
    Process GitHub extension files, determine the point of contact for each extension, and return the data as a DataFrame.

    Returns:
        pandas.DataFrame: A DataFrame containing extension data with ExtensionName, PointOfContact, and ExtensionPath.
    """
    gh_session = authenticate_github_session()
    extensions_data = []

    files = get_repository_files(gh_session)

    for file_meta_data in files:
        if file_meta_data['name'].endswith('.s4ext'):
            extension_path = file_meta_data['html_url'].split('/blob/main')[1]
            extension_name = file_meta_data['name'][:-6]
            logging.info("Processing extension: " + extension_name)
            # Get the content of the .s4ext file
            extension_file_content = gh_session.get(file_meta_data['download_url']).text
            point_of_contact = determine_point_of_contact(gh_session, extension_name, extension_file_content)
            extensions_data.append({'ExtensionName': extension_name, 'PointOfContact': point_of_contact, 'ExtensionPath': extension_path})

    df = pd.DataFrame(extensions_data)
    return df

result_df = process_extensions()

def generate_codeowners_file(extension_data, output_file="CODEOWNERS"):
    """
    Generate a CODEOWNERS file using the extension data and write it to a specified output file.

    Args:
        extension_data (pandas.DataFrame): A DataFrame containing extension data.
        output_file (str): The name of the output CODEOWNERS file.
    """
    with open(output_file, 'w') as codeowners_file:
        for index, row in extension_data.iterrows():
            point_of_contact = row['PointOfContact']
            if point_of_contact is not None:
                codeowners_file.write(f"{row['ExtensionPath']} {'@' + point_of_contact}\n")

if __name__ == "__main__":

    generate_codeowners_file(result_df, output_file="NEW_CODEOWNERS")
    logging.info('Generating CODEOWNERS file \n \n')
