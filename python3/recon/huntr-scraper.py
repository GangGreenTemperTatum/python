from enum import Enum
from rich.console import Console
from rich.style import Style
from rich.table import Table
from rich.logging import RichHandler

import requests
from requests.exceptions import RequestException, ConnectionError, Timeout
import time

from bs4 import BeautifulSoup
import os
import sys
import json
from pprint import pprint
from urllib.parse import unquote
import csv
import logging
from datetime import datetime
import subprocess
from subprocess import TimeoutExpired
from pathlib import Path

# Setup base directories
home_dir = Path.home()
base_dir = home_dir / "git" / "bounties"
log_dir = base_dir / "logs"
output_dir = base_dir / "output"
repos_dir = base_dir / "repositories"

# Create necessary directories
for directory in [log_dir, output_dir, repos_dir]:
    directory.mkdir(parents=True, exist_ok=True)

# Setup logging
log_filename = log_dir / f"log_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RichHandler(),
        logging.FileHandler(str(log_filename))
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

# Function to clone repositories
def clone_repo(org, repo):
    repo_path = repos_dir / org / repo
    
    if repo_path.exists():
        print_message(MessageType.WARN, f"Directory already exists: {repo_path}")
        return False
    
    repo_path.parent.mkdir(parents=True, exist_ok=True)
    clone_url = f"https://github.com/{org}/{repo}.git"
    
    try:
        subprocess.run(["git", "clone", clone_url, str(repo_path)], 
                       check=True, capture_output=True, text=True, timeout=30)
        print_message(MessageType.SUCCESS, f"Cloned repository: {clone_url} to {repo_path}")
        return True
    except TimeoutExpired:
        print_message(MessageType.FATAL, f"Cloning repository timed out after 30 seconds: {clone_url}")
        logging.error(f"Git clone timeout: {clone_url}")
        # Clean up the partially cloned repository
        if repo_path.exists():
            subprocess.run(["rm", "-rf", str(repo_path)])
        return False
    except subprocess.CalledProcessError as e:
        print_message(MessageType.FATAL, f"Failed to clone repository: {clone_url}")
        logging.error(f"Git clone error: {e.stderr}")
        return False

# Function for retrying requests
def make_request_with_retry(url, headers, error_message, max_retries=3, backoff_factor=0.3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except (ConnectionError, Timeout) as e:
            if attempt == max_retries - 1:
                print_message(MessageType.FATAL, f"{error_message}: {url}")
                logging.error(f"Connection error: {str(e)}")
                return None
            time.sleep(backoff_factor * (2 ** attempt))
        except RequestException as e:
            print_message(MessageType.FATAL, f"{error_message}: {url}")
            logging.error(f"Request error: {str(e)}")
            return None

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
table.add_column("Repo URL", justify="left", style="green", no_wrap=True)
table.add_column("Languages", justify="left", style="yellow", no_wrap=True)

# Open a CSV file to write the results
csv_filename = output_dir / f"huntr_repositories_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Organization", "Repo", "Repo URL", "Languages"])

    for organization, repo in repos:
        repo_url = f"{github_api_base_url}/{organization}/{repo}"
        print_message(MessageType.INFO, f"Requesting URL: {repo_url}")
        logging.info(f"Request Headers: {headers}")
        
        repo_response = make_request_with_retry(repo_url, headers, "Failed to fetch repository details")
        
        if repo_response is None:
            languages = "N/A"
        elif repo_response.status_code == 200:
            repo_data = repo_response.json()
            logging.info(f"Response JSON: {json.dumps(repo_data, indent=2)}")
            
            if 'organization' in repo_data:
                org_info = repo_data['organization']
                print_message(MessageType.SUCCESS, f"Repository: {repo}, Organization: {org_info['login']}")
                
                # Clone the repository
                cloned = clone_repo(organization, repo)
                
                # Fetch languages
                languages_url = f"{repo_url}/languages"
                languages_response = make_request_with_retry(languages_url, headers, "Failed to fetch languages")
                
                if languages_response and languages_response.status_code == 200:
                    languages_data = languages_response.json()
                    languages = ", ".join(languages_data.keys())
                else:
                    languages = "Failed to fetch"
            else:
                languages = "N/A"
                print_message(MessageType.WARN, f"Repository: {repo}, Organization: Not available")
        else:
            languages = "N/A"
            print_message(MessageType.FATAL, f"Failed to fetch details for repository: {repo}")
            logging.error(f"Response Status Code: {repo_response.status_code}")
            logging.error(f"Response Text: {repo_response.text}")
        
        # Add the result to the table
        table.add_row(organization, repo, repo_url, languages)
        
        # Write the result to the CSV file
        writer.writerow([organization, repo, repo_url, languages])

# Print the table to the console
CONSOLE.print(table)

# Save the table to a file
table_filename = output_dir / f"huntr_repositories_table_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
with open(table_filename, 'w') as f:
    table_text = CONSOLE.export_text()
    f.write(table_text)