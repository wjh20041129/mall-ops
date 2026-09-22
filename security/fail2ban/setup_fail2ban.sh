#!/bin/bash
# 一键部署 fail2ban 防爆破（4 台机器通用）
# 用法：sudo bash setup_fail2ban.sh

set -e

apt-get install -y fail2ban
cp jail.local /etc/fail2ban/jail.local
systemctl enable --now fail2ban

echo "=== fail2ban 状态 ==="
systemctl is-active fail2ban
fail2ban-client status sshd | head -8