# BlackBox exporter for prometheus

## - install BlackBox exporter in target server:
Connecting to a node over SSH:
Create blackbox_exporter user
```
useradd --no-create-home --shell /bin/false blackbox_exporter
```
install blackbox exporter
```
cd ~
curl -LO https://github.com/prometheus/blackbox_exporter/releases/download/v0.12.0/blackbox_exporter-0.12.0.linux-amd64.tar.gz
check checksums:
sha256sum blackbox_exporter-0.12.0.linux-amd64.tar.gz
Output
c5d8ba7d91101524fa7c3f5e17256d467d44d5e1d243e251fd795e0ab4a83605  blackbox_exporter-0.12.0.linux-amd64.tar.gz

tar xvf blackbox_exporter-0.12.0.linux-amd64.tar.gz
mv ./blackbox_exporter-0.12.0.linux-amd64/blackbox_exporter /usr/local/bin
chown blackbox_exporter:blackbox_exporter /usr/local/bin/blackbox_exporter
rm -rf ~/blackbox_exporter-0.12.0.linux-amd64.tar.gz ~/blackbox_exporter-0.12.0.linux-amd64

mkdir /etc/blackbox_exporter
chown blackbox_exporter:blackbox_exporter /etc/blackbox_exporter
touch /etc/blackbox_exporter/blackbox.yml
chown blackbox_exporter:blackbox_exporter /etc/blackbox_exporter/blackbox.yml
```
add below lines to <b>/etc/blackbox_exporter/blackbox.yml</B>
```
modules:
  http_2xx:
    prober: http
    timeout: 5s
    http:      
      valid_status_codes: []
      method: GET
```
make a service:
add below lines to <B>/etc/systemd/system/blackbox_exporter.service</B>
```
[Unit]
Description=Blackbox Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=blackbox_exporter
Group=blackbox_exporter
Type=simple
ExecStart=/usr/local/bin/blackbox_exporter --config.file /etc/blackbox_exporter/blackbox.yml

[Install]
WantedBy=multi-user.target
```

Run and check service:
```
chmod 664 /lib/systemd/system/mysqld_exporter.service
systemctl daemon-reload
systemctl start blackbox_exporter
systemctl status blackbox_exporter
systemctl enable blackbox_exporter
```
update firewall rules:
```
firewall-cmd --permanent --zone=public --add-port=9115/tcp
firewall-cmd --reload
```
Verify blackbox Exporter is Running:
```
http://<node_exporter-server-ip>:9115/metrics
http://<node_exporter-server-ip>:9115/probe
```

## - prometheus config
nano prometheus.yml
```
  - job_name: 'blackbox'
    metrics_path: /probe
    params:
      module: [http_2xx]  # Look for a HTTP 200 response.
    static_configs:
      - targets:
          - https://website1.com
          - https://website2.com:8093
          - http://website3.com
          - http://website4.com:8523
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: <node_exporter-server-ip>:9115
```
## - grafana dashboard
import json dashboard to grafana:
![image](https://github.com/user-attachments/assets/43e217f3-d435-48f7-9009-99c270a6a41d)


