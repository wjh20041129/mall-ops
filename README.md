# mall-ops 商城系统部署与运维项目

一个练手用的轻量商城系统，走通「代码 -> 容器化 -> 批量部署 -> 监控告警 -> 备份恢复」整条链路。

## 架构

```
浏览器
  │ http://web01:80
  ▼
Nginx (反向代理)
  │
  ▼
Flask 商城应用 (app:5000) ──→ MySQL 8 (mysql:3306, 数据卷持久化)
  │
  └──→ Redis 7 (缓存商品详情, 60s 过期)

controlNode: Ansible 控制机 + Prometheus + Grafana + node_exporter
web01/web02: Nginx + 应用容器
db01: MySQL + Redis
```

## 技术栈

| 技术 | 用途 |
|---|---|
| Linux (Ubuntu) | netplan 静态 IP、ufw 防火墙、crontab 定时任务、日志排查 |
| Docker / Compose | 应用、Nginx、MySQL、Redis 全容器化编排 |
| Ansible | SSH 免密 + inventory + ad-hoc 批量执行 + 简单 playbook |
| Prometheus + Grafana | 主机监控与可视化（node_exporter 采集） |
| Nginx | 反向代理（支线：负载均衡） |
| MySQL | 用户/商品/订单表，增删改查、多表联查、事务 |
| Redis | 商品详情缓存（setex + 过期时间） |
| Shell / Python | 备份脚本、健康检查脚本、定时清理；应用本身是 Python |

## 目录

```
app/        商城应用（Flask + 建表 SQL）
ansible/    批量部署配置
scripts/    备份、健康检查、日志清理脚本
monitor/    Prometheus 配置和告警规则
docs/       架构设计、部署手册、面试问答
```

## 快速开始

```bash
# 1. 起服务（web01 上执行）
docker compose up -d

# 2. 验证
curl http://localhost/            # 商品列表
curl http://localhost/goods/1     # 商品详情（首次查库，之后命中 Redis）

# 3. 看日志
docker compose logs -f app
```

MySQL 初始化数据在 `app/db.sql`，首次启动自动导入。默认用户 `admin / 123456`。

## 当前进度

- [x] 第一阶段（最小架构）：单实例部署 + 备份 + 基础监控
- [x] 第二阶段：Nginx 负载均衡（web01/web02 轮询）、fail2ban 防爆破
- [ ] 第三阶段（待做）：Alertmanager 告警、故障演练、Tomcat 点缀

## 负载均衡说明

web02 用 `docker-compose.app.yml` 跑独立应用容器（连 web01 的 MySQL/Redis），
web01 的 Nginx 通过 upstream 轮询分发（见 `nginx/default.conf`），
访问日志携带 `$upstream_addr`，刷新页面可从日志确认请求交替落在两台后端。