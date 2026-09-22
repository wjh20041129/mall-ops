# mall-ops 商城系统部署与运维项目

一个轻量商城系统，走通「代码 → 容器化 → 批量部署 → 监控告警 → 安全加固 → 备份恢复」整条链路。
部署环境为 4 台 Ubuntu 26.04 虚拟机（VMware NAT 网络）。

## 架构

4 台 Ubuntu 26.04 虚拟机（VMware NAT 内网 192.168.93.0/24），分工：

| 机器 | IP | 跑的容器 | 端口 |
|---|---|---|---|
| web01 | 192.168.93.101 | nginx + app + mysql + redis | 80 / 5000 / 3306 / 6379 |
| web02 | 192.168.93.102 | app（负载均衡第二节点） | 5000 |
| controlNode | 192.168.93.100 | prometheus + grafana（兼 Ansible 控制机） | 9090 / 3000 |
| db01 | 192.168.93.103 | 预留，暂未跑容器 | - |

请求流向：

```
浏览器 → web01:80 (nginx)
            ├── 轮询 → web01 的 app:5000
            └── 轮询 → web02 的 app:5000
                        └── 两个 app 连同一个 MySQL/Redis（在 web01 上），数据一致
```

监控：4 台机器都装了 node_exporter(9100)，controlNode 的 Prometheus 每 15s 抓一次，
Grafana 出面板（导入的 Node Exporter Full 模板）。MySQL/Redis 数据放 docker 数据卷，
容器删了数据不丢。

## 技术栈落点

| 技术 | 用在哪 | 相关文件 |
|---|---|---|
| Docker / Compose | 应用/网关/数据库/缓存全容器化；数据卷持久化 | `app/Dockerfile`、`docker-compose.yml` |
| Nginx | 反向代理 + upstream 轮询负载均衡，日志带 `$upstream_addr` 验证分发 | `nginx/default.conf` |
| Ansible | SSH 免密 + inventory 分组 + ad-hoc 批量执行 + playbook 批量装 Docker/node_exporter | `ansible/` |
| Prometheus + Grafana | 主机监控（node_exporter 采集 4 台），告警规则（CPU/内存/磁盘/宕机） | `monitor/` |
| MySQL | 3 张表（users/goods/orders），多表联查 JOIN、事务防超卖、索引 | `app/db.sql`、`app/app.py` |
| Redis | 商品详情缓存（setex 60s 过期），下单后删缓存保持一致性 | `app/app.py` |
| Linux | netplan 静态 IP、/etc/hosts 解析、systemctl、crontab、ufw、日志排查 | `docs/部署手册.md` |
| 安全 | fail2ban 防 SSH 爆破（实测 5 次失败封 IP），ufw 按角色放行端口 | `security/` |
| Shell | MySQL 备份（保留7天）、健康检查（异常自动重启）、日志清理 | `scripts/` |
| Git | 全程版本管理，演进式提交（见提交历史） | — |

## 目录

```
app/        商城应用（Flask + 建表 SQL + Dockerfile + 页面模板）
ansible/    inventory 分组、ad-hoc 命令记录、playbook（装 Docker/exporter/一键初始化）
monitor/    Prometheus 抓取配置 + 告警规则（alert.rules.yml）
nginx/      Nginx 负载均衡配置（upstream 轮询）
security/   fail2ban 配置 + 一键部署脚本
scripts/    backup.sh / health_check.sh / log_cleanup.sh + crontab 示例
docs/       架构设计、部署手册、面试问答、Redis 速成、fail2ban 实测
```

## 快速开始

```bash
# 1. 起服务（web01 上执行）
docker compose up -d

# 2. 验证
curl http://localhost/            # 商品列表
curl http://localhost/goods/1     # 商品详情（首次查库，之后命中 Redis）

# 3. 看日志（确认缓存命中/写入）
docker compose logs -f app
```

MySQL 初始化数据在 `app/db.sql`（首次启动自动导入），默认用户 `admin / 123456`。

## 关键设计

- **负载均衡**：web02 用 `docker-compose.app.yml` 起独立应用容器，连 web01 的 MySQL/Redis
- **缓存一致性**：商品详情 Redis 缓存 60s 过期；下单成功后主动 `r.delete` 清缓存，避免显示旧库存
- **防超卖**：下单事务里 `UPDATE goods SET stock=stock-N WHERE stock>=N`，影响行数为 0 即回滚
- **监控链路**：node_exporter(4台) → Prometheus → Grafana，告警规则见 `monitor/alert.rules.yml`
- **备份**：crontab 每天 2 点 mysqldump（`--single-transaction` 不锁表）+ gzip，保留 7 天

## 当前进度

- [x] 第一阶段：单机全栈部署 + 备份 + 基础监控
- [x] 第二阶段：Nginx 负载均衡（web01/web02 轮询）、fail2ban 防爆破
- [ ] 第三阶段（规划中）：Alertmanager 告警、数据库拆分到 db01、MySQL 主从、故障演练