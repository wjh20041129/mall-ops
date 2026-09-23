# mall-ops 商城系统部署与运维项目

**Docker + Ansible + Prometheus** 驱动的商城系统全链路部署与运维：4 台 Ubuntu 虚拟机，容器化部署商城，Nginx 负载均衡，自动化批量运维，主机监控告警，安全加固与自动备份。

## 技术栈

| 领域 | 技术 |
|---|---|
| 容器化 | Docker / Docker Compose（自研 Dockerfile 构建应用镜像） |
| 负载均衡 | Nginx（反向代理 + upstream 轮询双应用节点） |
| 自动化运维 | Ansible（SSH 免密 / inventory 分组 / ad-hoc / Playbook） |
| 监控告警 | Prometheus / node_exporter / Grafana（含告警规则） |
| 数据库 | MySQL（事务 / 多表联查 / 索引）、Redis（缓存） |
| 后端开发 | Python / Flask |
| 系统与网络 | Linux（Ubuntu）、Shell 脚本、Git |
| 安全加固 | fail2ban（防 SSH 爆破）/ UFW 防火墙 |

## 项目亮点

- 4 台 Ubuntu 机器部署完整商城，Nginx 轮询分发到双应用节点（web01/web02），共享同一套 MySQL/Redis，数据一致
- Ansible 批量初始化节点：装 Docker、装 node_exporter、配置 /etc/hosts（3 个 playbook + ad-hoc 实测）
- Prometheus 每 15s 抓取 4 台机器指标，Grafana 可视化面板，配置 CPU / 内存 / 磁盘 / 宕机告警规则
- 下单事务防超卖（条件扣库存 + 回滚）、Redis 缓存一致性（60s 过期 + 下单后主动清缓存）
- fail2ban 防爆破实测（错误密码 5 次封禁 IP）、MySQL 每日自动备份（保留 7 天）

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

## 目录

```
app/        商城应用（Flask + 建表 SQL + Dockerfile + 页面模板）
ansible/    inventory 分组、ad-hoc 记录、playbook（装 Docker / node_exporter / 一键初始化）
k8s/        k3s 集群部署清单（mysql/redis/app + 镜像加速配置）
monitor/    Prometheus 抓取配置 + 告警规则
nginx/      Nginx 负载均衡配置（upstream 轮询）
security/   fail2ban 配置 + 一键部署脚本
scripts/    backup.sh / health_check.sh / log_cleanup.sh + crontab 示例
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
- **缓存一致性**：商品详情 Redis 缓存 60s 过期；下单成功后主动删缓存，避免显示旧库存
- **防超卖**：下单事务里 `UPDATE goods SET stock=stock-N WHERE stock>=N`，影响行数为 0 即回滚
- **监控链路**：node_exporter(4台) → Prometheus → Grafana，告警规则见 `monitor/alert.rules.yml`
- **备份**：crontab 每天 2 点 mysqldump（`--single-transaction` 不锁表）+ gzip，保留 7 天

## 当前进度

- [x] 第一阶段：单机全栈部署 + 备份 + 基础监控
- [x] 第二阶段：Nginx 负载均衡（web01/web02 轮询）、fail2ban 防爆破
- [ ] 第三阶段（规划中）：Alertmanager 告警、数据库拆分、MySQL 主从、故障演练