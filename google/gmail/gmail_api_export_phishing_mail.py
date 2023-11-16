import base64
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# https://developers.google.com/gmail/api/guides
# https://developers.google.com/gmail/api/reference/rest/v1/users.labels
# https://developers.google.com/gmail/api/reference/rest/v1/users.messages/list
# https://developers.google.com/gmail/api/reference/rest/v1/users.messages/get

print("\nEnsure you have set the correct GCP project via 'gcloud config set project $PROJECT-ID' and the OAUTH API scopes have been set\n\n")


def get_gmail_service():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def get_label_id(service, user_id, label_name):
    try:
        labels = service.users().labels().list(
            userId=user_id).execute().get('labels', [])
        for label in labels:
            if label['name'].lower() == label_name.lower():
                return label['id']
        print(f'Label "{label_name}" not found.')
        return None
    except Exception as error:
        print(f'An error occurred: {error}')
        return None


def list_messages_with_label(service, user_id, label_id):
    try:
        response = service.users().messages().list(
            userId=user_id, labelIds=[label_id]).execute()
        messages = response.get('messages', [])
        return messages
    except Exception as error:
        print(f'An error occurred: {error}')
        return None


def save_messages_to_file(messages, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        for message in messages:
            msg_id = message['id']
            msg = service.users().messages().get(userId=user_id, id=msg_id).execute()
            if 'payload' in msg and 'headers' in msg['payload']:
                headers = msg['payload']['headers']
                subject = next(
                    (header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
                file.write(f'Subject: {subject}\n')
                file.write(f'---\n')
                body = msg['payload']['body']['data']
                file.write(base64.urlsafe_b64decode(body).decode('utf-8'))
                file.write('\n\n\n')


def save_messages_body_to_file(messages, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        for message in messages:
            msg_id = message['id']
            msg = service.users().messages().get(userId=user_id, id=msg_id).execute()
            if 'payload' in msg and 'body' in msg['payload']:
                body = msg['payload']['body']['data']
                file.write(base64.urlsafe_b64decode(body).decode('utf-8'))
                file.write('\n\n\n')


if __name__ == '__main__':
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    user_id = input('Enter your Gmail user ID (email address): ')
    label_name = 'phishing'
    output_file_messages = 'phishing_labelled_emails.txt'
    output_file_body = 'phishing_labelled_emails_body.txt'

    service = get_gmail_service()

    if service:
        label_id = get_label_id(service, user_id, label_name)
        if label_id:
            print(f'The label ID for "{label_name}" is: {label_id}')
            messages = list_messages_with_label(service, user_id, label_id)
            if messages:
                print(
                    f'Total {len(messages)} messages found with label "{label_name}".')
                save_messages_to_file(messages, output_file_messages)
                print(f'Messages saved to {output_file_messages}.')

                save_messages_body_to_file(messages, output_file_body)
                print(f'Messages body saved to {output_file_body}.')
            else:
                print(f'No messages found with label "{label_name}".')
