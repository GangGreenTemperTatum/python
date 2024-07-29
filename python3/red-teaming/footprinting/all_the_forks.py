import requests
import json
import os
import time

# Get the GitHub Personal Access Token from environment variable
gh_pat = os.getenv('GH_PAT')

if not gh_pat:
    print('Error: GH_PAT environment variable is not set. Please set the environment variable to run the script.' + '\n' + 'https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api?apiVersion=2022-11-28')
    exit(1)

# Prompt for the repository owner and name
owner = input('Enter the owner of the repository: ')
repo = input('Enter the name of the repository: ')
sha1 = input('Enter the SHA1 commit hash: ')

# Check if the SHA1 commit hash is greater than 40 characters
if len(sha1) > 40 or ' ' in sha1:
    print('Error: SHA1 commit hash cannot be greater than 40 characters and should not contain whitespace.')
    exit(1)

# Check if the SHA1 commit hash is greater than 6 characters
if len(sha1) > 6:
    sha1 = sha1[:6]
    print(f'Truncated SHA1 commit hash to: {sha1}')

print("Any forks commits results will be available at './all_the_forks_url.txt'")
time.sleep(1)  # Pause the script for one second to read the prompt

# Create a directory for storing commit JSON files if it doesn't exist
os.makedirs('./commits_blobs', exist_ok=True)

# Define the GitHub API URL for fetching forks
url = f'https://api.github.com/repos/{owner}/{repo}/forks'

# Set up the headers with the required authentication and API version
headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {gh_pat}',
    'X-GitHub-Api-Version': '2022-11-28'
}

# Make a GET request to the GitHub API to fetch the forks
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    forks = response.json()
    
    # Extract and print the full_name values
    fork_full_names = [fork['full_name'] for fork in forks]
    for full_name in fork_full_names:
        print(full_name)
    
    # Fetch commit details for each fork
    for full_name in fork_full_names:
        # Split the full_name to get owner and repo
        fork_owner, fork_repo = full_name.split('/')
        
        # Define the GitHub API URL for fetching the commit
        commit_url = f'https://api.github.com/repos/{fork_owner}/{fork_repo}/commits/{sha1}'
        
        # Make a GET request to the GitHub API to fetch the commit details
        commit_response = requests.get(commit_url, headers=headers)
        
        # Check if the request was successful
        if commit_response.status_code == 200:
            commit_data = commit_response.json()
            
            # Write commit data to a file
            with open(f'./commits_blobs/{fork_owner}_{fork_repo}_{sha1}commit.json', 'w') as f:
                json.dump(commit_data, f, indent=2)
            
            # Print success message to stdout
            success_message = f'Commit found for: {commit_url}'  + '\n' + f'saving JSON blob to {fork_owner}_{fork_repo}_{sha1}_commit.json' + '\n'
            print(success_message)
            
            # Write success message to a file
            with open('./all_the_forks_url.txt', 'a') as f:
                f.write(success_message + '\n')
        else:
            print(f'Failed to fetch commit for {full_name}: {commit_response.status_code}')
else:
    print(f'Failed to fetch forks: {response.status_code}')
