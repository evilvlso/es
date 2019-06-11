#!/usr/bin/env bash
sudo rpm --import https://packages.elastic.co/GPG-KEY-elasticsearch

cat <<- EOF > /etc/yum.repos.d/elastic.repo
[elastic-6.x]
name=Elastic repository for 6.x packages
baseurl=https://artifacts.elastic.co/packages/6.x/yum
gpgcheck=1
gpgkey=https://artifacts.elastic.co/GPG-KEY-elasticsearch
enabled=1
autorefresh=1
type=rpm-md
EOF

sudo yum install -y filebeat

sudo chkconfig --add filebeat

rm -rf /etc/filebeat/filebeat.yml

cat <<- EOF > /etc/filebeat/filebeat.yml
filebeat.prospectors:
  - type: log
    paths:
     - '/var/lib/docker/containers/*/*.log'
    document_type: tomcatlog
    tail_files: true
    processors:
     - add_docker_metadata: ~
    json.keys_under_root: false

processors:
  - decode_json_fields:
      fields: ["message"]

output.elasticsearch:
  hosts: ["10.32.32.140:9200"]
  index: "docker-logs-%{+yyyy.MM.dd}"

setup.template.name: "docker-logs"
setup.template.pattern: "docker-logs-*"
EOF

sudo service filebeat start
