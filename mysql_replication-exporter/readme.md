# mysql replication exporter
## 1. in replication server.             
- install dependencies:
```
   sudo apt update
   sudo apt install python3 python3-pip
   pip3 install mysql-connector-python flask
```
- create flask app:
  ```
  mkdir /root/exporter
  nano /root/exporter/mysql_replication-status.py
  ```
-  copy below code to mysql_replication-status.py:
  ```
import subprocess
from flask import Flask, Response
import threading
import time

app = Flask(__name__)

status = {
    'Slave_IO_Running': 0,
    'Slave_SQL_Running': 0
}

def fetch_mysql_status():
    global status
    while True:
        try:
            # Execute the MySQL command and capture the output
            result = subprocess.run(
                ["mysql", "-e", "SHOW REPLICA STATUS\\G"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0:
                print(f"Error executing mysql command: {result.stderr}")
            else:
                # Parse the output for Slave_IO_Running and Slave_SQL_Running
                io_running = 0
                sql_running = 0

                for line in result.stdout.splitlines():
                    if line.strip().startswith("Slave_IO_Running:"):
                        value = line.split(":")[1].strip()
                        io_running = 1 if value == "Yes" else 0
                    elif line.strip().startswith("Slave_SQL_Running:"):
                        value = line.split(":")[1].strip()
                        sql_running = 1 if value == "Yes" else 0

                status['Slave_IO_Running'] = io_running
                status['Slave_SQL_Running'] = sql_running
        except Exception as e:
            print(f"Unexpected error: {e}")

        # Sleep for 60 seconds before the next fetch
        time.sleep(60)

@app.route('/metrics', methods=['GET'])
def metrics():
    metrics = []
    metrics.append(f'mysql_slave_io_running {status["Slave_IO_Running"]}')
    metrics.append(f'mysql_slave_sql_running {status["Slave_SQL_Running"]}')

    return Response("\n".join(metrics), mimetype='text/plain')

if __name__ == '__main__':
    # Start the background thread to fetch MySQL status
    threading.Thread(target=fetch_mysql_status, daemon=True).start()
    # Run the Flask app
    app.run(host='0.0.0.0', port=9105)
  ```

> [!TIP]
> In this sample code, there is `no need` for a username and password to login to the mysql service.

- Now, test python app:
    ```
    python3 /root/exporter/mysql_replication-status.py
    ```
    
- start expoter as a service.
  copy below code to /etc/systemd/system/mysql_replication-status.service:
```
[Unit]
Description=MySQL Replication Status Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /root/exporter/mysql_replication-status.py
WorkingDirectory=/root/exporter
Restart=always
User=root

[Install]
WantedBy=multi-user.target
```

- start and enable service:
```
sudo systemctl daemon-reload
systemctl start mysql_replication-status.service
systemctl status mysql_replication-status.service
systemctl enable mysql_replication-status.service
```

- Check running exporter:
```
curl http://localhost:9105/metrics
```

## 2. prometheus config.
-  add below code to prometheus.yml:
```
  - job_name: 'mysql-rep'
    metrics_path: /metrics
    static_configs:
      - targets: ['replica-server-ip:9105']
        labels:
          server: replica-server
```

## 3. import json dashboard to grafana:
![image](https://github.com/user-attachments/assets/04b6743a-9588-4b1e-8523-e9e3757b17c7)
