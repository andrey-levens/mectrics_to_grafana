import sqlite3
import socket
from datetime import datetime
import time


def check_rtsp_stream(rtsp_url):
    try:
        from urllib.parse import urlparse
        parsed_url = urlparse(rtsp_url)
        ip = parsed_url.hostname
        port = parsed_url.port or 554  # Порт RTSP по умолчанию

        with socket.create_connection((ip, port), timeout=5):
            return 1  # Поток работает
    except Exception:
        return 0  # Поток не работает


def setup_database(db_name="rtsp_monitoring.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Создаем таблицу для хранения данных, если ее нет
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS device_status (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        check_time TEXT NOT NULL,
        device_ip TEXT NOT NULL,
        status INTEGER NOT NULL
    )
    """)

    conn.commit()
    return conn


def save_status_to_db(conn, check_time, device_ip, status):
    cursor = conn.cursor()

    # Вставляем данные в таблицу
    cursor.execute("""
    INSERT INTO device_status (check_time, device_ip, status)
    VALUES (?, ?, ?)
    """, (check_time, device_ip, status))

    conn.commit()


def monitor_multiple_rtsp(devices, interval=5, db_name="rtsp_monitoring.db"):
    # Настраиваем базу данных
    conn = setup_database(db_name)

    print(f"Начало мониторинга {len(devices)} устройств:")
    while True:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for device in devices:
            rtsp_url = f"rtsp://login:password@{device}/screenlive+audiodevice"
            status = check_rtsp_stream(rtsp_url)

            # Сохраняем данные в базу данных
            save_status_to_db(conn, current_time, device, status)

            print(f"[{current_time}] Устройство {device} - {'работает' if status == 1 else 'не работает'}")

        time.sleep(interval)


# Список устройств
devices = [
    "192.168.4.",
    "192.168.4.",
    "192.168.4.",
    "192.168.4.",
    "192.168.4.",
    "192.168.4.",
    "192.168.4.",
    "192.168.4.",
    "192.168.6.",
    "192.168.4.",
    "192.168.4.",
    "192.168.4.",
    "192.168.6.",
    "192.168.4."
]

# Запуск мониторинга
monitor_multiple_rtsp(devices, interval=5)
