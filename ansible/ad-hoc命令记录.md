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

---

# 实测输出（真实执行记录）

## 批量看负载

```
web02 | CHANGED | rc=0 >>
 15:56:37 up  1:07,  1 user,  load average: 0.00, 0.00, 0.00
web01 | CHANGED | rc=0 >>
 15:56:37 up  1:07,  1 user,  load average: 0.13, 0.06, 0.05
db01 | CHANGED | rc=0 >>
 15:56:37 up  1:07,  1 user,  load average: 0.00, 0.00, 0.00
```

## 批量看磁盘（web01 剩 3.9G，最先需要扩容的就是它）

```
db01 | CHANGED | rc=0 >>
/dev/mapper/ubuntu--vg-ubuntu--lv  9.8G  3.8G  5.5G  41% /
web02 | CHANGED | rc=0 >>
/dev/mapper/ubuntu--vg-ubuntu--lv  9.8G  3.5G  5.9G  38% /
web01 | CHANGED | rc=0 >>
/dev/mapper/ubuntu--vg-ubuntu--lv  9.8G  5.4G  3.9G  58% /
```

## 批量装 Docker（web02 就是用这条装起来的）

```
web02 | CHANGED | rc=0 >>
Docker version 29.1.3, build 29.1.3-0ubuntu4.1
Docker Compose version 2.40.3+ds1-0ubuntu1
```

## playbook 批量装 node_exporter（install_exporter.yml）

```
TASK [安装 prometheus-node-exporter] *****************
ok: [web01]
ok: [web02]
ok: [db01]

PLAY RECAP *******************************************
db01 : ok=3  changed=1  failed=0
web01: ok=3  changed=1  failed=0
web02: ok=3  changed=1  failed=0
```