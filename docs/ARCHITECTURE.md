# Employee360 Architecture

## Application Layers
1. Frontend: React, Vite and Nginx.
2. Backend: Python Flask and Gunicorn REST API.
3. Database: PostgreSQL 16.

## AWS Infrastructure
- AWS EC2 hosts the application and Kind cluster.
- A separate EC2 instance runs Jenkins.
- Instances communicate over the private VPC network.
- Security Groups control inbound access.

## CI/CD Flow
1. Developer pushes code to GitHub.
2. GitHub webhook triggers Jenkins.
3. Jenkins checks out the repository.
4. Jenkins builds frontend and backend Docker images.
5. Images are pushed to Docker Hub.
6. Jenkins connects to the application server through SSH.
7. Helm updates the Kubernetes deployment.
8. Kubernetes runs the updated application pods.

## Monitoring Flow
Kubernetes metrics are collected by Prometheus.
Grafana displays dashboards using Prometheus as its data source.
Alertmanager handles alert routing.
Node Exporter and kube-state-metrics provide infrastructure and Kubernetes metrics.
6. Jenkins connects to the application server through SSH.
7. Helm updates the Kubernetes deployment.
8. Kubernetes runs the updated application pods.

## Monitoring Flow
Kubernetes metrics are collected by Prometheus.
Grafana displays dashboards using Prometheus as its data source.
Alertmanager handles alert routing.
Node Exporter and kube-state-metrics provide infrastructure and Kubernetes metrics.
