import paramiko
from scp import SCPClient

REMOTE_USER = ''
REMOTE_HOST = ''
REMOTE_PASSWORD = ''
REMOTE_PATH = '/home/ftpuser/' 
LOCAL_PATH = '/mnt/nas/...' 

def create_ssh_client(hostname, username, password=None, port=92):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, password=password, port=port)
    return client

def get_latest_files(ssh_client, remote_path):
    stdin, stdout, stderr = ssh_client.exec_command(f'ls -t {remote_path} | head -n 2')
    files = stdout.read().decode().strip().split('\n')
    if files:
        return files
    else:
        raise FileNotFoundError("Не удалось найти файлы на удаленном сервере")

def download_and_delete_files(ssh_client, remote_path, local_path, files):
    with SCPClient(ssh_client.get_transport()) as scp:
        for file_name in files:
            file_name = file_name.strip()
            try:
                
                print(f"Загружаю файл: {file_name}")
                scp.get(remote_path + file_name, local_path)
                print(f"Файл {file_name} успешно скачан в {local_path}")
                print(f"Удаляю файл: {file_name} с сервера")
                ssh_client.exec_command(f'rm -f {remote_path}{file_name}')
                print(f"Файл {file_name} успешно удалён с сервера")

            except Exception as e:
                print(f"Ошибка при обработке файла {file_name}: {e}")

def main():
    ssh_client = None
    try:
        ssh_client = create_ssh_client(REMOTE_HOST, REMOTE_USER, REMOTE_PASSWORD)
        latest_files = get_latest_files(ssh_client, REMOTE_PATH)
        print(f"Последние файлы: {', '.join(latest_files)}")

        download_and_delete_files(ssh_client, REMOTE_PATH, LOCAL_PATH, latest_files)

    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        if ssh_client:
            ssh_client.close()

if __name__ == '__main__':
    main()
