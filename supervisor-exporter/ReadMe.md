# Supervisor exporter for prometheus

## - install supervisor exporter for nodes:
Connecting to a node over SSH
nano <B>/etc/supervisor/supervisord.conf</B>
```
[inet_http_server]
port = 127.0.0.1:9001
```
update supervisor
```
supervisorctl reread
supervisorctl update
```
and get go app
```
curl http://127.0.0.1:9001/RPC2
git clone https://github.com/salimd/supervisord_exporter.git
go build

mkdir -p /etc/supervisor/logs/
```
nano <B>/etc/supervisor/conf.d/supervisor-metrics.conf</B>
```
[program:supervisor-metrics]
process_name=%(program_name)s_%(process_num)02d
command=/root/supervisor/supervisord_exporter/supervisord_exporter -supervisord-url="http://127.0.0.1:9001/RPC2" -web.listen-address=":9200" -web.telemetry-path="/metrics"
autostart=true
autorestart=true
user=root
numprocs=1
redirect_stderr=true
stdout_logfile=/etc/supervisor/logs/supervisor-metrics.log
stopwaitsecs=3600
startsecs=0
```
update supervisor
```
supervisorctl reread
supervisorctl update
```
update firewall rules:
```
firewall-cmd --permanent --zone=public --add-port=9001/tcp
firewall-cmd --reload
```
Verify node exporter is Running:
```
http://<node_exporter-ip>:9200
http://<node_exporter-ip>:9200/metrics
```
> [!NOTE]
> Source: https://github.com/salimd/supervisord_exporter

## - prometheus config
nano prometheus.yml
```
  - job_name: 'supervisor'
    metrics_path: /metrics
    static_configs:
      - targets: ['<exporter-server-ip>:9200']
```
## - grafana dashboard
import json dashboard to grafana:
![image](https://github.com/user-attachments/assets/9f5754b3-b4c8-44ee-93f8-db448500df27)


