# Employee360 Deployment Guide

## Prerequisites
- AWS EC2 Ubuntu instances
- Docker and Docker Compose
- Jenkins with Docker Hub credentials
- Kubernetes Kind and kubectl
- Helm
- GitHub repository and webhook

## Application Deployment
The Jenkins pipeline builds and pushes versioned frontend and backend images to Docker Hub.

Jenkins then connects to the application server and runs Helm upgrade.

## Kubernetes Commands
Check cluster:
kubectl cluster-info

Check application pods:
kubectl get pods

Check services:
kubectl get services

Check Helm release:
helm status employee360

Check Helm history:
helm history employee360

Rollback:
helm rollback employee360 REVISION

## Application Access
Frontend: http://APP_SERVER_PUBLIC_IP:8081
