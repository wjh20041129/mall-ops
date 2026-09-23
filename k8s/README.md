# k8s

mall-ops 在 k3s 集群上的部署清单（双节点：k3s-master + k3s-worker）。

```bash
kubectl apply -f mysql.yaml   # mysql + pvc + db.sql 初始化
kubectl apply -f redis.yaml
kubectl apply -f app.yaml     # NodePort 30080 暴露
```

- 应用镜像 `mall-ops-app:v1` 本地构建后导入 containerd（`ctr -n k8s.io images import`）
- 镜像加速：k3s 节点 `/etc/rancher/k3s/registries.yaml` 指向 daocloud（见 registries.yaml）
- 实验记录：扩容 3 副本跨节点调度、删 Pod 自愈重建、env 变更滚动更新