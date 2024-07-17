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
