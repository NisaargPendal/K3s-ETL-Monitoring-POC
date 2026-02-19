# System Architecture: Top-Down View

This document provides a bird's-eye view of how the POC is structured across your laptop, the K3s cluster, and the individual components.

## 1. Visual System Map

This diagram illustrates the hierarchy from your physical machine down to the smallest containerized process.

```mermaid
graph TD
    %% Levels
    subgraph Host ["Level 0: Host Machine (Your Laptop)"]
        direction TB
        
        subgraph Runtimes ["Level 1: Runtimes & Infrastructure"]
            direction LR
            Docker["Docker Engine<br/>(Simulating External Services)"]
            K3sSvc["K3s System Service<br/>(Cluster Brain)"]
        end

        subgraph Cluster ["Level 2: K3s Virtual Cluster"]
            direction TB
            Node["K3s Single Node (ws-mio40rp8)"]
            
            subgraph Namespaces ["Level 3: Resource Isolation"]
                direction LR
                
                %% Project Namespace
                subgraph etl_poc ["Namespace: etl-poc"]
                    direction TB
                    MSSQL_Comp["MSSQL<br/>(Deployment)"]
                    ETL_Comp["ETL Puller<br/>(CronJob)"]
                    Storage[("MSSQL Data<br/>(PVC)")]
                    
                    MSSQL_Comp --- Storage
                end

                %% System Namespace
                subgraph kube_system ["Namespace: kube-system"]
                    direction TB
                    Logging["Fluent Bit<br/>(DaemonSet)"]
                    Monitoring["Monitoring Stack<br/>(Prometheus, Loki, Grafana)"]
                    Metrics["Kube-State-Metrics<br/>(Dep)"]
                    Networking["CoreDNS / Traefik<br/>(Networking)"]
                end
            end
        end

        %% External Connections
        ExternalDB[("Postgres DB<br/>(External Source)")]
        Docker --- ExternalDB
        
        %% Visualization
        Browser["Host Browser<br/>(Grafana UI)"]
    end

    %% Key Interactions
    ETL_Comp -.->|Pull| ExternalDB
    ETL_Comp -.->|Push| MSSQL_Comp
    Logging ===>|Loki Push| Monitoring
    Monitoring -.->|Scrape| Metrics
    Monitoring -.->|Scrape| ETL_Comp
    Browser -.->|View| Monitoring

    %% Styling
    classDef infra fill:#f5f5f5,stroke:#333,stroke-width:2px;
    classDef etl fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef system fill:#fff3e0,stroke:#ef6c00,stroke-width:2px;
    classDef storage fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef monitor fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px;

    class Docker,K3sSvc,Node infra;
    class ETL_Comp,MSSQL_Comp etl;
    class Logging,Networking system;
    class Storage,ExternalDB storage;
    class Monitoring,Metrics monitor;
```

---

## 2. Deployment Details & Statefulness

| Component | K8s Kind | Namespace | Statefulness | Role |
| :--- | :--- | :--- | :--- | :--- |
| **ETL App** | `CronJob` | `etl-poc` | **Stateless** | Runs Python logic to sync data every 5 mins. |
| **MSSQL** | `Deployment` | `etl-poc` | **Stateful** | Relational DB. Stores persistent data in a PVC. |
| **Prometheus** | `Deployment` | `kube-system` | **Stateful** | Metric storage and scraping engine. |
| **Loki** | `Deployment` | `kube-system` | **Stateful** | Log storage and indexing. |
| **Grafana** | `Deployment` | `kube-system` | **Stateless** | Visualization portal (connected to P&L). |
| **Fluent Bit** | `DaemonSet` | `kube-system` | **Stateless** | Log harvester; ships container logs to Loki. |
| **KSM** | `Deployment` | `kube-system` | **Stateless** | Kube-State-Metrics; converts K8s API objects to Prometheus metrics. |
| **Networking** | `Deployment` | `kube-system` | **Stateless** | CoreDNS and Traefik Ingress Controller. |
| **External DB** | `Container` | `Docker` | **Stateful** | Simulates the source ERP/external database. |

> ***Note on Persistence**: "Stateless" in Kubernetes doesn't mean it doesn't do anything—it means the **Pod** is disposable. If you lose a Pod, K8s makes a new one from the Blueprint (Image). **State** is only kept if it's stored in a **Volume (PVC)**.*
