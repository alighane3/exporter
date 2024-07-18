# Node exporter for prometheus

## - install node exporter for servers:
Connecting to a node over SSH
```
sudo groupadd -f node_exporter
sudo useradd -g node_exporter --no-create-home --shell /bin/false node_exporter
sudo mkdir /etc/node_exporter
sudo chown node_exporter:node_exporter /etc/node_exporter

wget https://github.com/prometheus/node_exporter/releases/download/v1.7.0/node_exporter-1.7.0.linux-amd64.tar.gz
tar xvfz node_exporter-*.*-amd64.tar.gz
cd node_exporter-*.*-amd64
cp node_exporter /usr/bin/
sudo chown node_exporter:node_exporter /usr/bin/node_exporter
```
make a service:
```
SERVICE_TEXT="[Unit]
 Description=Node Exporter
 Documentation=https://prometheus.io/docs/guides/node-exporter/
 Wants=network-online.target
 After=network-online.target

[Service]
 User=node_exporter
 Group=node_exporter
 Type=simple
 Restart=on-failure
 ExecStart=/usr/bin/node_exporter --web.listen-address=:9100

[Install]
 WantedBy=multi-user.target"

echo "$SERVICE_TEXT" | sudo tee /lib/systemd/system/node_exporter.service > /dev/null
```

Run and check service:
```
chmod 664 /lib/systemd/system/node_exporter.service

systemctl daemon-reload
systemctl start node_exporter
systemctl status node_exporter
systemctl enable node_exporter
```
update firewall rules:
```
firewall-cmd --permanent --zone=public --add-port=9100/tcp
firewall-cmd --reload
```
Verify node exporter is Running:
```
- in node server:
curl http://localhost:9100/metrics
- over internet:
http://<node_exporter-ip>:9100/metrics
```

## - prometheus config
nano prometheus.yml
```
  - job_name: 'node-exp'
    static_configs:
      - targets: ['<node_exporter-ip>:9100']
```
## - grafana dashboard
import json dashboard to grafana:


