from prometheus_client import start_http_server, Gauge, Info
import subprocess
import time
import sys
import re

# Настройки SNMP
snmp_host = ''
community = 'public'

# Определяем OID для различных метрик
oids = {
    'cpu_load': '1.3.6.1.4.1.24681.1.2.1.0',
    'disk_temperature_1': '1.3.6.1.4.1.24681.1.2.11.1.3.1',
    'disk_temperature_2': '1.3.6.1.4.1.24681.1.2.11.1.3.2',
    'disk_temperature_3': '1.3.6.1.4.1.24681.1.2.11.1.3.3',
    'disk_temperature_4': '1.3.6.1.4.1.24681.1.2.11.1.3.4',
    'disk_model_1': '1.3.6.1.4.1.24681.1.2.11.1.5.1',
    'disk_model_2': '1.3.6.1.4.1.24681.1.2.11.1.5.2',
    'disk_model_3': '1.3.6.1.4.1.24681.1.2.11.1.5.3',
    'disk_model_4': '1.3.6.1.4.1.24681.1.2.11.1.5.4',
    'disk_capacity_1': '1.3.6.1.4.1.24681.1.2.17.1.4.1',
    'disk_capacity_2': '1.3.6.1.4.1.24681.1.2.17.1.4.2',
    'disk_free_space_1': '1.3.6.1.4.1.24681.1.2.17.1.5.1',
    'disk_free_space_2': '1.3.6.1.4.1.24681.1.2.17.1.5.2',
    'disk_status_1': '1.3.6.1.4.1.24681.1.2.11.1.7.1',
    'disk_status_2': '1.3.6.1.4.1.24681.1.2.11.1.7.2',
    'disk_status_3': '1.3.6.1.4.1.24681.1.2.11.1.7.3',
    'disk_status_4': '1.3.6.1.4.1.24681.1.2.11.1.7.4',
    'fan_speed': '1.3.6.1.4.1.24681.1.2.15.1.3.1',
    'disk_format_1': '1.3.6.1.4.1.24681.1.2.17.1.3.1',
    'disk_format_2': '1.3.6.1.4.1.24681.1.2.17.1.3.2',
    'company_name': '1.3.6.1.4.1.24681.1.4.1.1.1.1.1.2.1.6.1'
}

# Определяем метрики для Prometheus
prometheus_metrics = {
    'cpu_load': Gauge('cpu_load', 'CPU Load', labelnames=['instance']),
    'disk_temperature': Gauge('disk_temperature', 'Disk Temperature in Celsius', labelnames=['instance', 'disk']),
    'disk_model': Info('disk_model', 'Disk Model', labelnames=['instance', 'disk']),
    'disk_capacity': Gauge('disk_capacity', 'Disk Capacity in TB', labelnames=['instance', 'disk']),
    'disk_free_space': Gauge('disk_free_space', 'Free Disk Space in TB', labelnames=['instance', 'disk']),
    'disk_status': Gauge('disk_status', 'Disk Health Status (1=GOOD, 0=BAD)', labelnames=['instance', 'disk']),
    'fan_speed': Gauge('fan_speed', 'Fan Speed in RPM', labelnames=['instance']),
    'disk_format': Info('disk_format', 'Disk Format', labelnames=['instance', 'disk']),
    'company_name': Info('company_name', 'Company Name', labelnames=['instance'])
}

def snmp_walk_single_oid(host, oid, community='public'):
    try:
        cmd = f"snmpwalk -v2c -c {community} {host} {oid}"
        result = subprocess.check_output(cmd, shell=True, text=True)

        snmp_response = []
        for line in result.splitlines():
            parts = line.split(" = ")
            if len(parts) == 2:
                oid_value = parts[1].strip().split(":")[-1].strip()  # Извлекаем значение после ":"
                snmp_response.append(oid_value)

        return snmp_response[-1] if snmp_response else None

    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении snmpwalk: {e}", file=sys.stderr)
        return None

def clean_value(value):
    cleaned_value = re.sub(r'[^\d.-]', '', value)
    try:
        return float(cleaned_value)
    except ValueError:
        return None

def extract_temperature(value):
    match = re.search(r'(\d+)\s*C', value)
    if match:
        return float(match.group(1))
    return None

if __name__ == '__main__':
    start_http_server(8002)
    print("Prometheus HTTP server started on port 8002")

    while True:
        for metric_name, oid in oids.items():
            oid_value = snmp_walk_single_oid(snmp_host, oid)

            if oid_value is not None:
                if 'temperature' in metric_name:
                    temp_value = extract_temperature(oid_value)
                    if temp_value is not None:
                        prometheus_metrics['disk_temperature'].labels(snmp_host, metric_name).set(temp_value)
                        print(f"Updated Prometheus metric for {metric_name}: {temp_value}")
                elif 'capacity' in metric_name or 'free_space' in metric_name:
                    cleaned_value = clean_value(oid_value)
                    if cleaned_value is not None:
                        prometheus_metrics['disk_capacity'].labels(snmp_host, metric_name).set(cleaned_value)
                        print(f"Updated Prometheus metric for {metric_name}: {cleaned_value}")
                elif 'status' in metric_name:
                    status_value = 1 if oid_value == "GOOD" else 0
                    prometheus_metrics['disk_status'].labels(snmp_host, metric_name).set(status_value)
                    print(f"Updated Prometheus disk status for {metric_name}: {status_value}")
                elif 'fan_speed' in metric_name:
                    fan_speed_value = clean_value(oid_value)
                    if fan_speed_value is not None:
                        prometheus_metrics['fan_speed'].labels(snmp_host).set(fan_speed_value)
                        print(f"Updated fan speed for {metric_name}: {fan_speed_value}")
                elif 'format' in metric_name:
                    prometheus_metrics['disk_format'].labels(snmp_host, metric_name).info({metric_name: oid_value})
                    print(f"Updated disk format for {metric_name}: {oid_value}")
                elif 'model' in metric_name:
                    prometheus_metrics['disk_model'].labels(snmp_host, metric_name).info({metric_name: oid_value})
                    print(f"Updated disk model for {metric_name}: {oid_value}")
                elif 'company_name' in metric_name:
                    prometheus_metrics['company_name'].labels(snmp_host).info({'name': oid_value})
                    print(f"Updated company name: {oid_value}")
                else:
                    cpu_value = clean_value(oid_value)
                    if cpu_value is not None:
                        prometheus_metrics['cpu_load'].labels(snmp_host).set(cpu_value)
                        print(f"Updated CPU load: {cpu_value}")
            else:
                print(f"Failed to retrieve SNMP data for {metric_name} ({oid})")

        time.sleep(15)
