# Employee360 — HRMS DevOps Project

Three-tier HRMS deployed on AWS EC2 using Docker, Jenkins, Docker Hub, Kubernetes Kind, Helm, Prometheus and Grafana..

## Technology Stack
- Frontend: React, Vite, Nginx
- Backend: Flask, Gunicorn
- Database: PostgreSQL 16
- CI/CD: Jenkins and GitHub Webhook
- Registry: Docker Hub
- Orchestration: Kubernetes Kind and Helm
- Monitoring: Prometheus, Grafana, Alertmanager

## Architecture
GitHub Push -> Webhook -> Jenkins -> Docker Build -> Docker Hub -> SSH -> App Server -> Kind -> Helm.

## Access URLs
- Application: http://APP_SERVER_PUBLIC_IP:8081
- Grafana: http://APP_SERVER_PUBLIC_IP:3000
- Prometheus: http://APP_SERVER_PUBLIC_IP:9090

## Local Setup
Configure .env using .env.example, then run docker compose up --build -d.

## Documentation
See docs/ARCHITECTURE.md, docs/DEPLOYMENT.md and docs/MONITORING.md.

Never commit real passwords, .env files, Docker tokens or SSH private keys.
See docs/ARCHITECTURE.md, docs/DEPLOYMENT.md and docs/MONITORING.md.

Never commit real passwords, .env files, Docker tokens or SSH private keys.
