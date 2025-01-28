from flask import Flask, jsonify
import paramiko

app = Flask(__name__)

@app.route('/restart_service', methods=['GET', 'POST'])
def restart_service():
    ip = '192.168.4.'  # IP сервера, на котором работает 1C
    username = ''  # Имя пользователя для SSH
    password = ''  # Пароль для SSH
    command = 'sudo systemctl restart srv1cv8-8.3.25.1374@default.service'  # Команда для перезапуска сервиса

    # Создаем объект SSH-клиента
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Устанавливаем SSH-соединение
        client.connect(ip, username=username, password=password)

        # Выполнение команды на сервере
        stdin, stdout, stderr = client.exec_command(command)

        # Чтение вывода и ошибок
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')

        # Проверка наличия ошибок
        if error:
            return jsonify({"status": "error", "message": error}), 500
        return jsonify({"status": "success", "message": output}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        # Закрытие соединения
        if client.get_transport() is not None and client.get_transport().is_active():
            client.get_transport().close()

        client.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7001)
