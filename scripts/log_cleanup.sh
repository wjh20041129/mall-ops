#!/bin/bash
# 清理 30 天前的业务日志
# crontab 里挂：0 3 * * 0 /root/scripts/log_cleanup.sh

log_dir=/var/log/mall
[ -d $log_dir ] || exit 0

find $log_dir -type f -name '*.log' -mtime +30 -delete
echo "$(date '+%F %T') 清理完成，剩余日志 $(ls $log_dir | wc -l) 个" >> /var/log/log_cleanup.log