# AWS deploy — CloudFormation + categorized GitHub workflows

Manually-triggered (`workflow_dispatch`) GitHub Actions that stand up VKP on **AWS EKS** using
**CloudFormation** for infra and `kubectl`/kustomize for the in-cluster workloads. The setup is
**categorized** so you can uninstall and reinstall one category at a time while the infra stays put.

CloudFormation (not Terraform) keeps stack state server-side in AWS — so a *separate* Destroy run
finds the stack by name and tears it down with no state backend to manage.

## Layers & categories

| Layer | Workflows | Stack / target | Notes |
|---|---|---|---|
| **Infra** (provision once, keep intact) | `AWS_001_Setup_Network` / `_Destroy_` | CFN `vkp-network` | VPC + 2 public subnets, IGW, **no NAT** (cost). `vpc_id` optional → reuse. |
| | `AWS_002_Setup_EKS` / `_Destroy_` | CFN `vkp-eks` | Cluster + managed nodegroup (**SPOT** `t3.medium` by default). |
| | `AWS_003_Setup_ECR` / `_Destroy_` | CFN `vkp-ecr` | 16 `vkp-*` repos (scan-on-push, keep-last-10, `EmptyOnDelete`). |
| **Build** | `AWS_004_Build_Push_Images` / `_Destroy_Images` | ECR | Builds all 16 images → ECR. Destroy purges images (repos stay). |
| **Workloads** (cherry-pick) | `AWS_005_Setup_Foundation` / `_Destroy_` | ns + ConfigMap + ingress + Secret | Bottom of the stack — its Destroy deletes the whole `vkp` namespace. |
| | `AWS_006_Setup_Data_Stores` / `_Destroy_` | postgres + mongo (in-cluster) | Destroy also deletes the PVCs (wipes data). |
| | `AWS_007_Setup_API_Services` / `_Destroy_` | 8 core backend services | company, user, airflow-adapter, guardrails, agentic, vector-config, context-engine, context-admin |
| | `AWS_008_Setup_Data_Mgmt` / `_Destroy_` | data pipeline + search | data-collection, ingestion, indexing, indexing-wfs, vehicle-explore |
| | `AWS_009_Setup_Portals` / `_Destroy_` | 3 Angular UIs | admin, search, cef |
| **Orchestrators** | `AWS_900_Run_All` | — | Runs 001→009 in dependency order. |
| | `AWS_901_Destroy_All` | — | Reverse. `scope=workloads` keeps infra; `scope=all` removes everything. |

Each module is BOTH `workflow_dispatch` (run it alone from the Actions tab) and `workflow_call`
(the orchestrators invoke the very same files). So "redeploy just the portals" = run
`AWS_009_Destroy_Portals` then `AWS_009_Setup_Portals` — the cluster, data, and other services are
untouched.

## GitHub secrets

Required (repo → Settings → Secrets and variables → Actions):

| Secret | Used by | Required |
|---|---|---|
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | all | yes |
| `AWS_SESSION_TOKEN` | all (STS only) | optional |
| `JWT_SECRET`, `DB_PASSWORD`, `VKP_SESSION_SECRET` | `AWS_005` → `vkp-secrets` | optional (sane defaults) |
| `OPENAI_API_KEY`, `GROQ_API_KEY` | `AWS_005` → `vkp-secrets` | optional (needed for live LLM answers) |

## Typical use

```text
# First bring-up (everything):
Actions → AWS_900_Run_All → Run workflow   (optionally set vpc_id, region, SPOT/ON_DEMAND, tag)

# Redeploy one category after a code change (infra + data untouched):
AWS_004_Build_Push_Images   (rebuild images at a new tag)
AWS_007_Destroy_API_Services → AWS_007_Setup_API_Services (image_tag=<new tag>)

# Tear down workloads but KEEP the cluster/VPC/ECR (stop paying for pods, keep infra warm):
AWS_901_Destroy_All  scope=workloads

# Nuke everything:
AWS_901_Destroy_All  scope=all
```

## Cost choices (deliberately cheap)

- **No NAT gateway** — nodes run in public subnets (saves ~$32/mo/NAT).
- **SPOT** worker nodes, small `t3.medium`, 20 GiB disk (override per run).
- **In-cluster** Postgres/Mongo instead of RDS/DocumentDB.
- **No cloud LoadBalancer** — the ingress objects are inert without an ingress controller; reach
  services with `kubectl port-forward` (zero extra AWS cost). Install an ingress controller yourself
  if you want a public endpoint (adds an ELB/NLB).
- ECR keep-last-10 lifecycle caps image storage.

The only always-on cost is the EKS control plane (~$0.10/hr). Run `AWS_901_Destroy_All scope=all`
when done to drop it.

## `vpc_id` reuse

`AWS_001` takes an optional `vpc_id`. Blank → it creates `vkp-vpc` (and re-runs are idempotent, so a
created VPC is reused). Provided → it creates only the EKS-tagged subnets inside that VPC and relies on
the VPC's existing internet egress (its main route table / IGW); the VPC itself is left intact on destroy.
