# Employee 360 — Complete HRMS + DevOps project

A three-tier HR management application built with React/Vite, Flask REST API and PostgreSQL.
It includes employee management, departments, attendance, leave workflows, payroll records,
performance reviews, recruitment, onboarding, notifications, authentication and role-based access..

## 1. Run locally

Requirements: Docker Engine/Desktop and Docker Compose v2.

```bash
cp .env.example .env
# Change SECRET_KEY and DB_PASSWORD before use.
docker compose up --build
```

Open:
- UI: http://localhost:8080
- API health: http://localhost:5000/api/health
- API metrics: http://localhost:5000/api/metrics

First-run demo accounts (change passwords immediately; demo only):
- admin@employee360.local / Admin@12345
- hr@employee360.local / Hr@12345
- manager@employee360.local / Manager@12345
- employee@employee360.local / Employee@12345

The database seeds demo accounts and synthetic records on first initialization.

## 2. Architecture

- Tier 1: React SPA served by Nginx.
- Tier 2: Flask REST API served by Gunicorn.
- Tier 3: PostgreSQL with a persistent Docker volume.
- Nginx proxies `/api/*` from the browser container to the API service.
- Compose health checks gate startup on database readiness.

## 3. API overview

Authentication:
- `POST /api/auth/login`
- `GET /api/auth/me`

Dashboard and core:
- `GET /api/dashboard`
- `GET/POST /api/employees`
- `GET/PUT/DELETE /api/employees/<id>`
- `GET/POST /api/departments`
- `GET/POST /api/attendance`
- `POST /api/attendance/check-in`
- `POST /api/attendance/check-out`
- `GET/POST /api/leaves`
- `POST /api/leaves/<id>/decision`
- `GET/POST /api/payroll`
- `GET/POST /api/performance`
- `GET/POST /api/jobs`
- `GET/POST /api/candidates`
- `GET/POST /api/onboarding`
- `GET /api/notifications`
- `GET /api/metrics`

All API routes except login and health require a bearer token. Mutating HR actions use role checks.

## 4. DevOps project roadmap

1. Local development: Docker Compose.
2. Source control: GitHub branches, pull requests and code review.
3. CI: GitHub Actions runs backend tests and frontend build.
4. Image build: Docker images tagged with commit SHA.
5. Registry: Amazon ECR.
6. Infrastructure: AWS VPC, private/public subnets, IAM roles, security groups.
7. Runtime: EKS or EC2-based Kubernetes; use managed PostgreSQL (RDS) for production.
8. Deployment: Kubernetes manifests and Helm chart.
9. Observability: Prometheus metrics; add Grafana dashboards and log aggregation.
10. Security: secrets manager, TLS ingress, image scanning, least privilege and backups.

## 5. Kubernetes / Helm

The sample Kubernetes files deploy the web and API tiers. PostgreSQL is intentionally not deployed
as an in-cluster StatefulSet for production. Use Amazon RDS PostgreSQL (or another managed,
backed-up PostgreSQL service) and supply `DATABASE_URL` through a Kubernetes Secret.

For a test cluster:
```bash
kubectl create namespace employee360
kubectl create secret generic employee360-secrets -n employee360 \
  --from-literal=DATABASE_URL='postgresql://USER:PASSWORD@RDS_ENDPOINT:5432/employee360' \
  --from-literal=SECRET_KEY='REPLACE_WITH_LONG_RANDOM_SECRET'
helm upgrade --install employee360 deploy/helm/employee360 -n employee360 \
  --set image.repository=YOUR_ACCOUNT.dkr.ecr.ap-south-1.amazonaws.com/employee360 \
  --set image.tag=YOUR_TAG
```
Build and push frontend and backend as separate images in a real deployment; the sample chart
shows the API and web image values separately.

## 6. Important production limitations

This is a functional learning MVP, not a certified payroll or statutory HR platform.
Before real use, add formal security review, strong password rotation, MFA/SSO, audit trails,
field-level privacy controls, encryption at rest/in transit, CSRF strategy where applicable,
rate limiting, file malware scanning, retention policies, statutory payroll/tax calculations,
approval delegation, database migrations, backup/restore drills and legal review.
Do not upload real employee identity, salary, health or bank data to this demo.

## Feature scope notes
The delivered HR modules provide working starter workflows and data screens. Payroll is a
recording/calculation MVP (not statutory payroll); recruitment includes job and candidate
records; onboarding includes task tracking; performance includes review records. File upload,
payslip PDF generation, tax/benefit rules, biometric attendance, email/SMS delivery, candidate
Kanban drag-and-drop and employee self-service profile editing are extension tasks.
