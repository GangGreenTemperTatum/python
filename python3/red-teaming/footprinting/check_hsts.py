import requests
def check_hsts(host):
    try:
        response = requests.get(f'https://{host}', timeout=5)
        hsts_header = response.headers.get('Strict-Transport-Security', None)

        if hsts_header:
            print(f'{host} has HSTS header: {hsts_header}')
        else:
            print(f'{host} does not have HSTS header.')

    except requests.ConnectionError:
        print(f'Connection error for {host}')

def main():
    file_path = 'host_list.txt'  # Change this to the path of your file
    with open(file_path, 'r') as file:
        hosts = file.read().splitlines()

    for host in hosts:
        check_hsts(host)

if __name__ == "__main__":
    main()
