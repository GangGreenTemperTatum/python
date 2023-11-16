import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# https://developers.google.com/gmail/api/guides
# https://developers.google.com/gmail/api/reference/rest/v1/users.labels
# https://developers.google.com/gmail/api/reference/rest/v1/users.messages/list
# https://developers.google.com/gmail/api/reference/rest/v1/users.messages/get

print("\nEnsure you have set the correct GCP project via 'gcloud config set project $PROJECT-ID' and the OAUTH API scopes have been set\n\n")


def authenticate_gmail_api():
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def get_message_content(service, user_id, message_id):
    try:
        message = service.users().messages().get(userId=user_id, id=message_id).execute()
        return message['snippet']
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def main():
    email = input("Enter your Google Email (Gmail): ")
    message_ids_file = input("Enter the path to the file containing line-separated Message IDs: ")
    output_file = input("Enter the path to the output file: ")

    creds = authenticate_gmail_api()
    service = build('gmail', 'v1', credentials=creds)

    with open(message_ids_file, 'r') as file:
        message_ids = file.read().splitlines()

    with open(output_file, 'w') as output:
        for message_id in message_ids:
            content = get_message_content(service, email, message_id)
            if content:
                output.write(content + '\n')

    print(f"Message content has been successfully retrieved and saved to {output_file}.")

if __name__ == '__main__':
    main()

