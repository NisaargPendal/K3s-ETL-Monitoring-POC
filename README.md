# 🚀 K3s ETL Monitoring POC

A comprehensive Proof of Concept (POC) demonstrating a containerized ETL pipeline running on **K3s** (Lightweight Kubernetes), featuring production-grade **Logging** and **Observability**.

## 🌐 Live Architecture Showcase
Check out the interactive system architecture here:
👉 **[https://nisaargpendal.github.io/K3s-ETL-Monitoring-POC/](https://nisaargpendal.github.io/K3s-ETL-Monitoring-POC/)**

---

## 🏗️ Project Overview
This project simulates a real-world enterprise data flow:
1.  **Source**: An external PostgreSQL database (running in Docker) containing raw 'orders'.
2.  **ETL Logic**: A Python-based CronJob that pulls data, filters for `confirmed` status, and performs an upsert.
3.  **Sink**: An internal MSSQL (SQL Server) instance running inside the K3s cluster.
4.  **Monitoring**: A full-stack observability layer using **Prometheus**, **Loki**, and **Grafana**, with **Fluent Bit** for log aggregation.

### Key Technical Features
- **Containerization**: Everything runs in Docker/K3s.
- **Infrastructure as Code**: All K8s manifests, RBAC, and storage configurations included.
- **Log Aggregation**: Fluent Bit harvests logs and ships them to Loki with Kubernetes metadata.
- **Dynamic Dashboards**: Custom Grafana dashboards with "Container-Wise" log filtering.
- **Stateful Storage**: PVC-backed storage for both MSSQL and Monitoring data.

---

## 📂 Project Structure
- `etl/`: Python application code and Dockerfile.
- `k8s/`: Kubernetes manifests for Deployment, Logging, and Monitoring.
- `external-db/`: Docker Compose for the source database.
- `docs/`: Technical documentation and Architecture visualizer.
- `scripts/`: Automation scripts for cluster installation and app application.

---

## 🛠️ How to View
For a deep dive into the implementation and usage, refer to the **[Project Structure Map](docs/project_structure.md)** and the **[Architecture Documentation](docs/architecture.md)**.

---

## 👨‍💻 Resume Ready
This POC highlights skills in:
- **Kubernetes (K3s)** & **Docker**
- **Data Engineering / ETL** (Python, SQL)
- **SRE / Observability** (Prometheus, Grafana, Loki, Fluent Bit)
- **Database Management** (PostgreSQL, MSSQL)
- **Platform Engineering** (RBAC, PVC, Namespacing)
