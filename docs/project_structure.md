# Project Structure & Deep Overall Status

This document maps every file in the `K3s-poc` repository to its specific responsibility, providing a "deep" view of the system's moving parts.

## 1. Directory Tree

```text
K3s-poc/
├── etl/                        # Core ETL Application
│   ├── Dockerfile              # Build instructions for the Python app
│   ├── etl_app.py              # Main sync logic (Source -> Filter -> Sink)
│   └── requirements.txt        # Python dependencies (psycopg2, pymssql)
├── external-db/                # External Source Simulation
│   ├── docker-compose.yml      # Runs Postgres on the host machine
│   └── init.sql                # Seeds the source 'orders' table
├── k8s/                        # Kubernetes Manifests
│   ├── etl-cronjob.yaml        # Schedule & Pod definition for the ETL app
│   ├── logging/                # Log Aggregation Layer
│   │   ├── fluent-bit-config.yaml
│   │   ├── fluent-bit-ds.yaml  # Collector (one per node)
│   │   └── rbac.yaml           # Permissions for logs
│   ├── monitoring/             # Monitoring & Observability Stack
│   │   ├── grafana-deployment.yaml
│   │   ├── grafana-dashboards.yaml # Pre-loaded Dashboard JSONs
│   │   ├── loki-deployment.yaml    # Log Storage
│   │   ├── prometheus-deployment.yaml # Metric Storage
│   │   └── kube-state-metrics.yaml # Cluster-level metric reporter
│   ├── mssql.yaml              # Internal Destination DB
│   ├── mssql-init-job.yaml     # One-time DB/Table setup for MSSQL
│   ├── secrets.yaml            # DB Credentials & Connection strings
│   ├── storage.yaml            # Persistent Volumes for Database data
│   └── namespace.yaml          # Logic isolation (etl-poc)
├── docs/                       # Architecture & Walkthroughs
│   ├── architecture.md         # Technical Top-Down View
│   └── architecture.html       # Visual Showcase Version
├── scripts/                    # Automation
│   ├── install-k3s.sh          # One-click Cluster Setup
│   └── apply-all.sh            # One-click Cluster Deployment
│── CHECKLIST.md                # Development Progress Tracker
```

## 2. Core Operational Flow

| Layer | Responsibility | Key Files |
| :--- | :--- | :--- |
| **Source** | Holds orders (`confirmed`, `pending`, etc.) | `external-db/`, `init.sql` |
| **Logic** | Pulls from Source, Filters confirmed, Pushes to Sink | `etl/etl_app.py`, `etl-cronjob.yaml` |
| **Sink** | Stores 'Confirmed' orders permanently | `k8s/mssql.yaml`, `k8s/storage.yaml` |
| **Observability** | Watches Pod health, CPU/RAM, and live logs | `k8s/monitoring/`, `k8s/logging/` |
| **Management** | Visualization and Dashboarding | `grafana-dashboards.yaml`, `etl-poc-dashboard.json` |

---

## 3. Deployment Status

- **Container Images**: All images (ETL app, MSSQL, P&L&G) are either standard official images or custom locally-built versions (`etl-app:v2`) imported directly into the K3s container runtime.
- **Data Persistence**: Managed via `hostPath` volumes on the local machine, ensuring database content survives Pod restarts.
- **Networking**: All components communicate via internal K8s Service DNS (e.g., `mssql-svc.etl-poc.svc.cluster.local`).
- **Monitoring**: Live end-to-end. Prometheus scrapes metrics every 15s; Fluent Bit ships logs instantly to Loki.
