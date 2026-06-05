# Infra

Deployment infrastructure for VKP: container images, Kubernetes manifests, and Terraform. This is
the **cloud/cluster** path — for the localhost dev loop use `npm run localhost:*` (see the root
README and `DevOps/Localhost/`).

```
Infra/
  docker/        # Dockerfiles per service archetype (java / python / angular) + nginx.conf
  k8s/
    base/        # all app workloads + ConfigMap + Secret template + Ingress
    overlays/dev # image registry + tags
    platform/    # in-cluster Postgres+pgvector + MongoDB (self-contained clusters)
    secrets/     # External Secrets + SOPS examples (production secret sourcing)
  terraform/     # The same app deployment as IaC (kubernetes provider, DRY for_each)
.github/workflows/build-images.yml   # CI: builds + pushes all 11 images to GHCR
```

## 1. Build images

CI does this automatically on push to `main` / tags (`.github/workflows/build-images.yml` →
`ghcr.io/<owner>/vkp-*`). To build locally:

```bash
# Java (context = Middleware/, so the build installs the shared libs first; JAR_PATH is relative to it)
docker build -f Infra/docker/java-service.Dockerfile \
  --build-arg SERVICE=indexing-service \
  --build-arg JAR_PATH=indexing-service/api/target/indexing-service.jar \
  -t ghcr.io/javakishore-veleti/vkp-indexing-service:dev Middleware
# the wfs-java executor is the same SERVICE with JAR_PATH=indexing-service/wfs-java/target/indexing-service-wfs-java.jar

# Python (context = the service root)
docker build -f Infra/docker/python-service.Dockerfile \
  -t ghcr.io/javakishore-veleti/vkp-vehicle-explore-service:dev Middleware/vehicle-explore-service

# Angular portal (context = the portal root)
docker build -f Infra/docker/angular-portal.Dockerfile \
  --build-arg PROJECT=admin-portal -t ghcr.io/javakishore-veleti/vkp-admin-portal:dev Portals/admin-portal
```

## 2a. Deploy with Kustomize (`Infra/k8s/`)

```bash
kubectl apply -k Infra/k8s/base                      # namespace + secret template + workloads
kubectl apply -k Infra/k8s/platform -n vkp           # OPTIONAL: in-cluster Postgres + Mongo
kubectl apply -k Infra/k8s/overlays/dev              # (or this instead of base, to pin images)
```

`base/` holds the Namespace, a shared **ConfigMap** (inter-service URLs, DB/OTEL config), a
**Secret** template, an **Ingress** (replaces the dev `proxy.conf.json` routing — `admin.vkp.local`
+ `app.vkp.local`), and a Deployment+Service per workload. `overlays/dev` pins the image registry +
tag. Validate without a cluster: `kubectl kustomize Infra/k8s/overlays/dev`.

## 2b. Deploy with Terraform (`Infra/terraform/`)

Same app topology as IaC — one `for_each` over a service map drives every Deployment + Service.

```bash
cd Infra/terraform
cp terraform.tfvars.example terraform.tfvars   # fill secrets (gitignored)
terraform init && terraform apply
```

## Databases (`Infra/k8s/platform/`)

- **Self-contained cluster (dev):** `kubectl apply -k Infra/k8s/platform -n vkp` deploys Postgres
  (pgvector, with the `vector` extension auto-created) + MongoDB as StatefulSets with PVCs, at the
  DNS names the ConfigMap expects (`postgres`, `mongodb`).
- **Production:** skip `platform/` and use **managed** databases (RDS/Cloud SQL Postgres+pgvector,
  MongoDB Atlas for vector search) — point the app ConfigMap / tfvars at their endpoints.
- Airflow + the observability backend (`jaeger-collector`) are likewise platform deps (managed or
  deployed separately).

## Secrets (`Infra/k8s/secrets/`)

`base/secret.example.yaml` is a placeholder for quick starts only. For real environments use one of:

- **External Secrets Operator** — `secrets/external-secret.example.yaml` materialises the same
  `vkp-secrets` Secret from a cloud secrets manager (AWS/GCP/Azure/Vault). Drop-in: the Deployments
  read it via `envFrom` unchanged.
- **SOPS** — `secrets/.sops.yaml` encrypts only the `data`/`stringData` of `secret.yaml` so the
  ciphertext can be committed and decrypted at apply time.

Never commit a real `secret.yaml` or `terraform.tfvars` (both gitignored). `JWT_SECRET` and
`VKP_SESSION_SECRET` must be identical across all services. Java services run the **`postgres`**
Spring profile in-cluster (H2 is dev-only).
