# Mysql exporter for prometheus

## - install mysql exporter for nodes:
Connecting to a node over SSH
```
MYSQL_EXPORTER_VERSION=$(curl -sL https://api.github.com/repos/prometheus/mysqld_exporter/releases/latest | grep "tag_name"   | sed -E 's/.*"([^"]+)".*/\1/'|sed 's/v//')
wget https://github.com/prometheus/mysqld_exporter/releases/download/v$MYSQL_EXPORTER_VERSION/mysqld_exporter-$MYSQL_EXPORTER_VERSION.linux-amd64.tar.gz
tar xvf mysqld_exporter*.tar.gz
cd mysqld_exporter*.*-amd64
cp mysqld_exporter /usr/bin/
```
nano <B>/etc/mysqld_exporter.cnf</B>
```
[client]
user=exporter
password=StrongPassssss
```
create mysql user:
```
mysql -u root -p
CREATE USER 'exporter'@'localhost' IDENTIFIED BY 'StrongPassssss' WITH MAX_USER_CONNECTIONS 3;
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'exporter'@'localhost';
FLUSH PRIVILEGES;
```
make a service:
add below lines to <B>/lib/systemd/system/mysqld_exporter.service</B>
```
[Unit]
Description=Prometheus MySQL Exporter
After=network.target

[Service]
Type=simple
Restart=always
ExecStart=/usr/bin/mysqld_exporter \
--config.my-cnf /etc/mysqld_exporter.cnf \
--collect.global_status \
--collect.info_schema.innodb_metrics \
--collect.auto_increment.columns \
--collect.info_schema.processlist \
--collect.binlog_size \
--collect.info_schema.tablestats \
--collect.global_variables \
--collect.info_schema.query_response_time \
--collect.info_schema.userstats \
--collect.info_schema.tables \
--collect.perf_schema.tablelocks \
--collect.perf_schema.file_events \
--collect.perf_schema.eventswaits \
--collect.perf_schema.indexiowaits \
--collect.perf_schema.tableiowaits \
--collect.slave_status \
--web.listen-address=0.0.0.0:9104

[Install]
WantedBy=multi-user.target
```

Run and check service:
```
chmod 664 /lib/systemd/system/mysqld_exporter.service
systemctl daemon-reload
systemctl start mysqld_exporter
systemctl status mysqld_exporter
systemctl enable mysqld_exporter
```
update firewall rules:
```
firewall-cmd --permanent --zone=public --add-port=9104/tcp
firewall-cmd --reload
```
Verify mysql exporter is Running:
```
curl http://localhost:9104/metrics
```

## - prometheus config
nano prometheus.yml
```
  - job_name: 'mysql'
    static_configs:
      - targets: ['node1-ip:9104']
        labels:
          server: node1
      - targets: ['node2-ip:9104']
        labels:
          server: node2
```
## - grafana dashboard
import json dashboard to grafana:
![image](https://github.com/user-attachments/assets/15012bd8-6920-48e2-84bd-e237cee42bf4)

