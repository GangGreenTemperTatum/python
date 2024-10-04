from enum import Enum
from rich.console import Console
from rich.style import Style
from rich.table import Table
from rich.logging import RichHandler

import requests
from bs4 import BeautifulSoup
import os
import sys
import json
from pprint import pprint
from urllib.parse import unquote
import csv
import logging
from datetime import datetime

# Setup logging
log_filename = f"log_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RichHandler(),
        logging.FileHandler(log_filename)
    ]
)

CONSOLE = Console(record=True)

# Define the message types
class MessageType(Enum):
    SUCCESS = "success"
    WARN = "warn"
    FATAL = "fatal"
    INFO = "info"

# Define the styles with emojis
styles = {
    MessageType.SUCCESS: Style(color="green", bold=False),
    MessageType.WARN: Style(color="yellow", bold=False),
    MessageType.FATAL: Style(color="red", bold=False, underline=True),
    MessageType.INFO: Style(color="blue", bold=False)
}

# Define the emojis
emojis = {
    MessageType.SUCCESS: ":white_check_mark:",  # ✅
    MessageType.WARN: ":warning:",  # ⚠️
    MessageType.FATAL: ":x:",  # ❌
    MessageType.INFO: ":information_source:",  # ℹ️
}

# Function to print messages with styles and emojis
def print_message(message_type, message):
    style = styles.get(message_type, Style())
    emoji = emojis.get(message_type, "")
    CONSOLE.print(f"{emoji} {message}", style=style)
    logging.info(f"{emoji} {message}")

# Check if the GitHub token is set
github_token = os.getenv('GITHUB_TOKEN')
if not github_token:
    print_message(MessageType.FATAL, "Error: GITHUB_TOKEN environment variable is not set.")
    sys.exit(1)

# Make a GET request to the URL
url = 'https://huntr.com/bounties'
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find all bounty items
bounty_items = soup.find_all('div', class_='group flex flex-row')

# Extract and print the organization and repo information
repos = []
for item in bounty_items:
    # Extract organization from img tag
    img_tag = item.find('img', alt='Repo')
    if img_tag:
        src_url = img_tag['src']
        decoded_url = unquote(src_url)
        organization = decoded_url.split('/')[-1].split('.')[0]
    
    # Extract repo from span tag
    span_tag = item.find('span')
    if span_tag:
        repo = span_tag.text.strip()
    
    if organization and repo:
        print_message(MessageType.INFO, f"Organization: {organization}, Repo: {repo}")
        repos.append((organization, repo))

# GitHub API base URL
github_api_base_url = 'https://api.github.com/repos'

# GitHub headers
headers = {
    'Authorization': f'Bearer {github_token}',
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28'
}

# Create a table for console output
table = Table(title="GitHub Repositories")
table.add_column("Organization", justify="left", style="cyan", no_wrap=True)
table.add_column("Repo", justify="left", style="magenta", no_wrap=True)
table.add_column("Status", justify="left", style="green", no_wrap=True)

# Open a CSV file to write the results
csv_filename = f"huntr_repositories_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Organization", "Repo", "Status"])

    # Fetch organization information for each repo repository
    for organization, repo in repos:
        repo_url = f"{github_api_base_url}/{organization}/{repo}"
        print_message(MessageType.INFO, f"Requesting URL: {repo_url}")
        logging.info(f"Request Headers: {headers}")
        
        repo_response = requests.get(repo_url, headers=headers)
        
        if repo_response.status_code == 200:
            repo_data = repo_response.json()
            # Pretty-print the response JSON
            logging.info(f"Response JSON: {json.dumps(repo_data, indent=2)}")
            
            # Extract and print the organization information
            if 'organization' in repo_data:
                org_info = repo_data['organization']
                status = repo_url
                print_message(MessageType.SUCCESS, f"Repository: {repo}, Organization: {org_info['login']}")
            else:
                status = repo_url
                print_message(MessageType.WARN, f"Repository: {repo}, Organization: Not available")
        else:
            status = repo_url
            print_message(MessageType.FATAL, f"Failed to fetch details for repository: {repo}")
            logging.error(f"Response Status Code: {repo_response.status_code}")
            logging.error(f"Response Text: {repo_response.text}")
        
        # Add the result to the table
        table.add_row(organization, repo, status)
        
        # Write the result to the CSV file
        writer.writerow([organization, repo, status])

# Print the table to the console
CONSOLE.print(table)

# Save the table to a file
table_filename = f"table_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
with open(table_filename, 'w') as f:
    table_text = CONSOLE.export_text()
    f.write(table_text)
