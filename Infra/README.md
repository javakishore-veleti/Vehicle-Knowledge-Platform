# Infra

Deployment infrastructure for VKP: container images, Kubernetes manifests, and Terraform. This is
the **cloud/cluster** path — for the localhost dev loop use `npm run localhost:*` (see the root
README and `DevOps/Localhost/`).

```
Infra/
  docker/        # Dockerfiles per service archetype (java / python / angular) + nginx.conf
  k8s/           # Kustomize: base/ (all workloads) + overlays/dev (image tags)
  terraform/     # The same deployment as IaC (kubernetes provider, DRY for_each)
```

## 1. Build images (`Infra/docker/`)

One Dockerfile per archetype; pass the service via build args.

```bash
# Java (context = Middleware/, so the build can install the shared libs first)
docker build -f Infra/docker/java-service.Dockerfile \
  --build-arg SERVICE=indexing-service --build-arg JAR=indexing-service.jar \
  -t ghcr.io/javakishore-veleti/vkp-indexing-service:dev Middleware

# Python (context = the service root)
docker build -f Infra/docker/python-service.Dockerfile \
  -t ghcr.io/javakishore-veleti/vkp-vehicle-explore-service:dev Middleware/vehicle-explore-service

# Angular portal (context = the portal root)
docker build -f Infra/docker/angular-portal.Dockerfile \
  --build-arg PROJECT=admin-portal -t ghcr.io/javakishore-veleti/vkp-admin-portal:dev Portals/admin-portal
```

## 2a. Deploy with Kustomize (`Infra/k8s/`)

```bash
cp Infra/k8s/base/secret.example.yaml Infra/k8s/base/secret.yaml   # fill real values (gitignored)
kubectl apply -k Infra/k8s/overlays/dev
```

`base/` holds the Namespace, a shared **ConfigMap** (inter-service URLs, DB/OTEL config), a
**Secret** template (JWT/session/DB/LLM keys), an **Ingress** (replaces the dev `proxy.conf.json`
routing — `admin.vkp.local` + `app.vkp.local`), and a Deployment+Service per workload. `overlays/dev`
pins the image registry + tag. Validate without a cluster: `kubectl kustomize Infra/k8s/overlays/dev`.

## 2b. Deploy with Terraform (`Infra/terraform/`)

Same topology as IaC — one `for_each` over a service map drives every Deployment + Service.

```bash
cd Infra/terraform
cp terraform.tfvars.example terraform.tfvars   # fill secrets (gitignored)
terraform init && terraform apply
```

## Assumptions

- **Databases + Airflow + observability are platform dependencies**, expected in-cluster at the DNS
  names the ConfigMap uses (`postgres`, `mongodb`, `jaeger-collector`) or as managed services
  (point the ConfigMap/tfvars at their endpoints). They are not (re)created here — provision them
  separately (managed Postgres+pgvector, MongoDB Atlas, a tracing backend).
- Java services run the **`postgres`** Spring profile in-cluster (H2 is dev-only).
- Secrets are placeholders. In production use Sealed Secrets / External Secrets / SOPS / cloud KMS —
  never commit `secret.yaml` or `terraform.tfvars`.
- `JWT_SECRET` and `VKP_SESSION_SECRET` must be identical across all services.
