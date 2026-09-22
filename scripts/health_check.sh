#!/bin/bash
# 网站健康检查，挂了就重启应用容器
# crontab 里挂：*/5 * * * * /root/scripts/health_check.sh

url=http://127.0.0.1/
out=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 $url)
echo "$(date '+%F %T') http_code=$out" >> /var/log/health_check.log

if [ "$out" != "200" ]; then
    echo "$(date '+%F %T') 检测到异常，重启 app 容器" >> /var/log/health_check.log
    docker restart mall-app
fi