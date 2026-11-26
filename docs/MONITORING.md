# Employee360 Monitoring Guide

## Monitoring Stack
Installed using the Prometheus Community kube-prometheus-stack Helm chart.

Components:
- Prometheus: collects and stores metrics.
- Grafana: visualizes metrics in dashboards.
- Alertmanager: manages alert notifications.
- Node Exporter: collects node-level metrics.
- kube-state-metrics: exposes Kubernetes object metrics.

## Access
Grafana: http://APP_SERVER_PUBLIC_IP:3000
Prometheus: http://APP_SERVER_PUBLIC_IP:9090

Grafana default username: admin.
Retrieve the password from the Kubernetes secret:
kubectl get secret monitoring-grafana -n monitoring -o jsonpath="{.data.admin-password}" | base64 -d

## Useful Commands
kubectl get pods -n monitoring
kubectl get services -n monitoring
helm status monitoring -n monitoring

## Example Prometheus Queries
Running pods:
kube_pod_status_phase{namespace="default",phase="Running"}

CPU usage:
sum(rate(container_cpu_usage_seconds_total{namespace="default",container!=""}[5m]))

Memory usage:
sum(container_memory_working_set_bytes{namespace="default",container!=""})

Pod restarts:
sum(kube_pod_container_status_restarts_total{namespace="default"})

## Dashboard
Employee360 - Kubernetes Monitoring dashboard includes pod status, CPU, memory, restarts and readiness panels.

## Kind Limitation
Some control-plane targets such as etcd, kube-controller-manager, kube-proxy and kube-scheduler may show DOWN because their metrics endpoints are not exposed by the Kind configuration. Other targets can remain UP.
