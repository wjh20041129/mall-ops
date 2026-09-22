#!/bin/bash
# MySQL 备份脚本（容器版），保留最近 7 天
# crontab 里挂：0 2 * * * /root/scripts/backup.sh

backup_dir=/backup/mysql
mkdir -p $backup_dir
date_str=$(date +%Y%m%d_%H%M%S)
file=$backup_dir/mall_$date_str.sql.gz

# --single-transaction 不加锁备份 InnoDB
docker exec mall-mysql sh -c 'mysqldump -umall -pmall123 --single-transaction mall' | gzip > $file

if [ $? -eq 0 ] && [ -s $file ]; then
    echo "$(date '+%F %T') backup ok: $(basename $file)" >> /var/log/backup.log
else
    echo "$(date '+%F %T') backup FAILED" >> /var/log/backup.log
    exit 1
fi

# 清理 7 天前的备份
find $backup_dir -name '*.sql.gz' -mtime +7 -delete