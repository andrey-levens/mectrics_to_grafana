import os
import time
import csv

# Путь к директории с бэкапами 1С
backup_directory = '/mnt/nas/...'
# Имя базы данных для проверки
db_name = 'name_db'
# Путь к CSV файлу для записи данных
csv_file = '/root/scripts/buh_don.csv'

def get_last_backup_info(directory, db_name):
    """Функция для получения информации о последнем бэкапе для указанной базы данных."""
    try:
        # Список для хранения файлов бэкапов
        backup_files = []

        # Проходим по всем файлам в директории
        for filename in os.listdir(directory):
            # Проверяем, соответствует ли имя файла шаблону для базы данных
            if filename.endswith(f"_{db_name}.tar"):
                full_path = os.path.join(directory, filename)
                backup_files.append(full_path)

        # Если бэкапы найдены, получаем последний
        if backup_files:
            # Сортируем файлы по времени модификации
            latest_backup_file = max(backup_files, key=os.path.getmtime)
            backup_time = os.path.getmtime(latest_backup_file)
            backup_size = os.path.getsize(latest_backup_file)

            # Преобразуем время бэкапа в локальное время
            local_time = time.localtime(backup_time)
            backup_time_readable = time.strftime('%Y-%m-%d %H:%M:%S', local_time)

            return backup_time_readable, backup_size, latest_backup_file
        else:
            return None, None, None

    except Exception as e:
        print(f"Ошибка: {e}")
        return None, None, None

def write_backup_info_to_csv(backup_info, csv_file):
    """Функция для записи данных о бэке в CSV файл."""
    # Проверяем, существует ли уже файл CSV
    file_exists = os.path.isfile(csv_file)

    # Записываем данные в CSV
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        # Если файл еще не существует, добавляем заголовки
        if not file_exists:
            writer.writerow(['Database Name', 'Backup Time', 'Backup Size (bytes)', 'Backup File'])

        # Записываем данные
        writer.writerow(backup_info)

if __name__ == "__main__":
    # Получаем информацию о последнем бэке
    backup_time, backup_size, backup_file = get_last_backup_info(backup_directory, db_name)

    # Выводим информацию о бэке и записываем в CSV
    if backup_time and backup_size:
        print(f"Последний бэкап для '{db_name}':")
        print(f"Время: {backup_time}")
        print(f"Размер: {backup_size} байт")
        print(f"Файл: {backup_file}")

        # Записываем данные в CSV
        write_backup_info_to_csv([db_name, backup_time, backup_size, backup_file], csv_file)
        print(f"Данные о бэке записаны в {csv_file}!")
    else:
        print(f"Бэкап для '{db_name}' не найден.")

