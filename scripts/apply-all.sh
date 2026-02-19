#!/usr/bin/env bash
# ============================================================
# apply-all.sh
# Applies all K8s manifests in the correct order
# Run this AFTER K3s is installed and ETL image is imported
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="$SCRIPT_DIR/../k8s"

echo "=============================="
echo " Applying K8s Manifests"
echo "=============================="

echo ""
echo "→ [1/6] Namespace..."
kubectl apply -f "$K8S_DIR/namespace.yaml"

echo ""
echo "→ [2/6] Secrets..."
kubectl apply -f "$K8S_DIR/secrets.yaml"

echo ""
echo "→ [3/6] Storage (PVC)..."
kubectl apply -f "$K8S_DIR/storage.yaml"

echo ""
echo "→ [4/6] Internal Postgres..."
kubectl apply -f "$K8S_DIR/postgres.yaml"

echo ""
echo "→ Waiting for Postgres to be ready (up to 60s)..."
kubectl rollout status deployment/postgres -n etl-poc --timeout=60s

echo ""
echo "→ [5/6] ETL CronJob..."
kubectl apply -f "$K8S_DIR/etl-cronjob.yaml"

echo ""
echo "→ [6/6] Public NodePort Service (for PowerBI/host access)..."
kubectl apply -f "$K8S_DIR/postgres-public-svc.yaml"

echo ""
echo "=============================="
echo " All manifests applied!"
echo ""
echo " Useful commands:"
echo "   kubectl get all -n etl-poc"
echo "   kubectl get pods -n etl-poc"
echo "   kubectl get svc -n etl-poc"
echo ""
echo " Manually trigger ETL:"
echo "   kubectl create job etl-test-\$(date +%s) --from=cronjob/etl-puller -n etl-poc"
echo ""
echo " Connect to internal DB from host:"
echo "   psql -h localhost -p 30543 -U int_user -d internal_db"
echo "   Password: int_password"
echo "=============================="
