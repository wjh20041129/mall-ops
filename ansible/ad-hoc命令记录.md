# ad-hoc 命令记录

## 连通性测试
ansible all -m ping

## 批量执行命令
ansible all -m shell -a "uptime"
ansible webs -m shell -a "df -h /"

## 批量拷贝文件（比如把脚本分发到各机器）
ansible all -m copy -a "src=/root/scripts/health_check.sh dest=/root/scripts/"

## 批量装软件包（Ubuntu 用 apt 模块，-b 是提权）
ansible all -m apt -a "name=htop state=present" -b

## 批量管理服务
ansible all -m systemd -a "name=prometheus-node-exporter state=started enabled=yes" -b

## 批量看 Docker 容器状态
ansible webs -m shell -a "docker ps" -b

## 常用参数
# -i 指定 inventory 文件
# -b 用 sudo 提权
# -K 提示输入 sudo 密码
# --limit 只对部分主机执行，如 --limit web01