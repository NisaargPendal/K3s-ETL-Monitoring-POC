#!/usr/bin/env bash
# ============================================================
# install-k3s.sh
# Installs K3s (single-node) on your local machine
# ============================================================
set -euo pipefail

echo "=============================="
echo " K3s Installation Script"
echo "=============================="

# Check if already installed
if command -v k3s &>/dev/null; then
  echo "✓ K3s is already installed: $(k3s --version)"
  exit 0
fi

echo "→ Downloading and installing K3s..."
curl -sfL https://get.k3s.io | sh -

echo ""
echo "→ Waiting for K3s to be ready..."
sleep 10

# Set up kubeconfig for current user
echo "→ Setting up kubeconfig..."
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown "$(id -u):$(id -g)" ~/.kube/config
export KUBECONFIG=~/.kube/config

echo ""
echo "→ Verifying cluster..."
kubectl get nodes

echo ""
echo "=============================="
echo " K3s Installed Successfully!"
echo " Run: export KUBECONFIG=~/.kube/config"
echo " Or add it to your ~/.bashrc / ~/.zshrc"
echo "=============================="
