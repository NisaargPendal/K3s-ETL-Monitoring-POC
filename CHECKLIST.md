# K3s ETL POC — Master Checklist

## Architecture Summary
- **External DB** → Simulated locally via Docker (Postgres container with dummy data)
- **K3s Cluster** → Runs on your local machine
- **Internal DB** → Postgres inside K3s with persistent local storage
- **ETL App** → Python script in a CronJob: pulls from external DB → filters → writes to internal DB
- **Ingress** → Traefik (built into K3s) exposes internal DB for read access (PowerBI simulation)

---

## Phase 1: Prerequisites — Install Required Tools

- [ ] 1.1 Install K3s (single-node cluster)
- [ ] 1.2 Verify K3s is running (`kubectl get nodes`)
- [ ] 1.3 Verify Docker is running (`docker ps`)
- [ ] 1.4 Install `psql` client for manual DB verification
- [ ] 1.5 Verify `kubectl` is pointing to K3s cluster

---

## Phase 2: External DB Setup (Simulated, via Docker)

- [ ] 2.1 Create `external-db/init.sql` — schema + dummy data
- [ ] 2.2 Create `external-db/docker-compose.yml` — Postgres container
- [ ] 2.3 Start external DB container (`docker compose up -d`)
- [ ] 2.4 Verify external DB is accessible (`psql` from host)
- [ ] 2.5 Verify dummy data is present in external DB

---

## Phase 3: K3s Namespace and Secrets

- [ ] 3.1 Create `k8s/namespace.yaml` — `etl-poc` namespace
- [ ] 3.2 Create `k8s/secrets.yaml` — external-db-creds + internal-db-creds
- [ ] 3.3 Apply namespace (`kubectl apply -f k8s/namespace.yaml`)
- [ ] 3.4 Apply secrets (`kubectl apply -f k8s/secrets.yaml`)
- [ ] 3.5 Verify secrets exist (`kubectl get secrets -n etl-poc`)

---

## Phase 4: Internal Postgres DB (Inside K3s)

- [ ] 4.1 Create `k8s/storage.yaml` — PVC using local-path provisioner
- [ ] 4.2 Create `k8s/postgres.yaml` — Deployment + ClusterIP Service
- [ ] 4.3 Apply storage (`kubectl apply -f k8s/storage.yaml`)
- [ ] 4.4 Apply postgres (`kubectl apply -f k8s/postgres.yaml`)
- [ ] 4.5 Verify Postgres pod is Running (`kubectl get pods -n etl-poc`)
- [ ] 4.6 Verify Postgres service is up (`kubectl get svc -n etl-poc`)

---

## Phase 5: ETL Application

- [ ] 5.1 Create `etl/etl_app.py` — pull, filter, write logic
- [ ] 5.2 Create `etl/requirements.txt` — Python dependencies
- [ ] 5.3 Create `etl/Dockerfile` — containerize the ETL app
- [ ] 5.4 Build Docker image (`docker build -t etl-app:latest ./etl`)
- [ ] 5.5 Import image into K3s (`k3s ctr images import ...`)
- [ ] 5.6 Create `k8s/etl-cronjob.yaml` — CronJob manifest
- [ ] 5.7 Apply CronJob (`kubectl apply -f k8s/etl-cronjob.yaml`)
- [ ] 5.8 Manually trigger a Job to test (`kubectl create job ...`)
- [ ] 5.9 Check ETL pod logs (`kubectl logs <pod> -n etl-poc`)

---

## Phase 6: Ingress / Expose Internal DB (Traefik)

- [ ] 6.1 Create `k8s/postgres-public-svc.yaml` — NodePort/LoadBalancer Service
- [ ] 6.2 Apply service (`kubectl apply -f k8s/postgres-public-svc.yaml`)
- [ ] 6.3 Verify external access to internal DB from host (`psql -h localhost -p <port>`)

---

## Phase 7: End-to-End Verification

- [ ] 7.1 Confirm external DB has source data
- [ ] 7.2 Trigger ETL job manually
- [ ] 7.3 Confirm filtered data appears in internal DB
- [ ] 7.4 Confirm internal DB is reachable from host (simulating PowerBI)
- [ ] 7.5 Let CronJob run on schedule and verify it repeats correctly

---

## File Tree (What We Will Create)

```
K3s-poc/
├── CHECKLIST.md                  ← This file
│
├── external-db/
│   ├── docker-compose.yml        ← Spins up the "external" Postgres
│   └── init.sql                  ← Creates schema + inserts dummy data
│
├── etl/
│   ├── etl_app.py                ← ETL logic (pull → filter → push)
│   ├── requirements.txt          ← psycopg2-binary
│   └── Dockerfile                ← Containerizes the ETL app
│
├── k8s/
│   ├── namespace.yaml            ← etl-poc namespace
│   ├── secrets.yaml              ← DB credentials as K8s Secrets
│   ├── storage.yaml              ← PVC for internal Postgres
│   ├── postgres.yaml             ← Internal Postgres Deployment + ClusterIP Service
│   ├── etl-cronjob.yaml          ← ETL CronJob
│   └── postgres-public-svc.yaml  ← Exposes internal DB externally (NodePort)
│
└── scripts/
    ├── install-k3s.sh            ← K3s installation script
    └── apply-all.sh              ← Applies all K8s manifests in order
```
