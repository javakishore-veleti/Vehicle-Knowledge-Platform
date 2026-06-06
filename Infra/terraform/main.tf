terraform {
  required_version = ">= 1.5"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.27"
    }
  }
}

provider "kubernetes" {
  config_path    = var.kubeconfig
  config_context = var.kube_context != "" ? var.kube_context : null
}

# ---------------------------------------------------------------------------
# Service catalogue. One map drives all Deployments + Services (DRY for_each),
# mirroring Infra/k8s/base/*.yaml. Probe path + resources derive from `kind`.
# ---------------------------------------------------------------------------
locals {
  defaults_by_kind = {
    java   = { probe = "/actuator/health", cpu = "250m", mem_req = "512Mi", mem_lim = "1Gi" }
    python = { probe = "/health", cpu = "250m", mem_req = "512Mi", mem_lim = "2Gi" }
    portal = { probe = "/", cpu = "50m", mem_req = "64Mi", mem_lim = "128Mi" }
  }

  services_raw = {
    company-service = { image = "vkp-company-service", port = 8081, kind = "java" }
    user-service    = { image = "vkp-user-service", port = 8082, kind = "java" }
    airflow-adapter = { image = "vkp-airflow-adapter-service", port = 8083, kind = "java" }
    data-collection = { image = "vkp-data-collection-service", port = 8084, kind = "java" }
    ingestion       = { image = "vkp-ingestion-service", port = 8085, kind = "java" }
    indexing        = { image = "vkp-indexing-service", port = 8086, kind = "java" }
    indexing-wfs    = { image = "vkp-indexing-wfs", port = 8087, kind = "java" }
    vector-config   = { image = "vkp-vector-config-service", port = 8088, kind = "java" }
    vehicle-explore = { image = "vkp-vehicle-explore-service", port = 8090, kind = "python" }
    guardrails      = { image = "vkp-guardrails-service", port = 8091, kind = "python" }
    agentic         = { image = "vkp-agentic-service", port = 8092, kind = "python" }
    context-engine  = { image = "vkp-context-engine-service", port = 8093, kind = "python" }
    context-admin   = { image = "vkp-context-admin-service", port = 8094, kind = "java" }
    admin-portal    = { image = "vkp-admin-portal", port = 80, kind = "portal" }
    search-portal   = { image = "vkp-vehicle-search-portal", port = 80, kind = "portal" }
  }

  services = {
    for name, s in local.services_raw : name => merge(s, local.defaults_by_kind[s.kind], {
      image_ref = "${var.image_registry}/${s.image}:${var.image_tag}"
    })
  }
}

resource "kubernetes_namespace_v1" "vkp" {
  metadata {
    name   = var.namespace
    labels = { "app.kubernetes.io/part-of" = "vehicle-knowledge-platform" }
  }
}

resource "kubernetes_config_map_v1" "vkp_config" {
  metadata {
    name      = "vkp-config"
    namespace = kubernetes_namespace_v1.vkp.metadata[0].name
  }
  data = {
    SPRING_PROFILES_ACTIVE             = "postgres"
    SPRING_DATASOURCE_URL              = "jdbc:postgresql://postgres:5432/vkp"
    SPRING_DATASOURCE_USERNAME         = "vkp"
    AIRFLOW_ADAPTER_BASE_URL           = "http://airflow-adapter:8083"
    INDEXING_WFS_BASE_URL              = "http://indexing-wfs:8087"
    INDEXING_DATA_COLLECTION_BASE_URL  = "http://data-collection:8084"
    INDEXING_AIRFLOW_CALLBACK_BASE_URL = "http://indexing:8086"
    DATACOLLECTION_COMPANY_SERVICE_URL = "http://company-service:8081"
    WFS_CONTROL_BASE_URL               = "http://indexing:8086"
    WFS_DC_BASE_URL                    = "http://data-collection:8084"
    VKP_PG_HOST                        = "postgres"
    VKP_PG_PORT                        = "5432"
    VKP_PG_DB                          = "vkp"
    VKP_PG_USER                        = "vkp"
    VKP_MONGO_URI                      = "mongodb://mongodb:27017/vkp"
    WFS_PG_URL                         = "jdbc:postgresql://postgres:5432/vkp"
    WFS_MONGO_URI                      = "mongodb://mongodb:27017/vkp"
    VKP_GUARDRAILS_URL                 = "http://guardrails:8091"
    VKP_VECTOR_STORE                   = "pgvector"
    VKP_SEARCH_MODE                    = "vector"
    OTEL_EXPORTER_OTLP_ENDPOINT        = "http://jaeger-collector:4318/v1/traces"
    VKP_OTEL_ENDPOINT                  = "http://jaeger-collector:4318"
    VKP_TRACE_SAMPLING                 = "0.1"
    VKP_JWT_ENABLED                    = "true"
  }
}

resource "kubernetes_secret_v1" "vkp_secrets" {
  metadata {
    name      = "vkp-secrets"
    namespace = kubernetes_namespace_v1.vkp.metadata[0].name
  }
  type = "Opaque"
  data = {
    JWT_SECRET                 = var.jwt_secret
    VKP_SESSION_SECRET         = var.session_secret
    SPRING_DATASOURCE_PASSWORD = var.db_password
    VKP_PG_PASSWORD            = var.db_password
    WFS_PG_PASSWORD            = var.db_password
    OPENAI_API_KEY             = var.openai_api_key
    GROQ_API_KEY               = var.groq_api_key
  }
}

resource "kubernetes_deployment_v1" "svc" {
  for_each = local.services

  metadata {
    name      = each.key
    namespace = kubernetes_namespace_v1.vkp.metadata[0].name
    labels    = { app = each.key, tier = each.value.kind }
  }
  spec {
    replicas = 1
    selector { match_labels = { app = each.key } }
    template {
      metadata { labels = { app = each.key, tier = each.value.kind } }
      spec {
        security_context { run_as_non_root = true }
        container {
          name  = each.key
          image = each.value.image_ref
          port { container_port = each.value.port }

          env {
            name  = "PORT" # the python-service image listens on $PORT (default 8080); java ignores it
            value = tostring(each.value.port)
          }

          # Backend services get the shared config + secret env; portals are static.
          dynamic "env_from" {
            for_each = each.value.kind == "portal" ? [] : [1]
            content {
              config_map_ref { name = kubernetes_config_map_v1.vkp_config.metadata[0].name }
            }
          }
          dynamic "env_from" {
            for_each = each.value.kind == "portal" ? [] : [1]
            content {
              secret_ref { name = kubernetes_secret_v1.vkp_secrets.metadata[0].name }
            }
          }

          readiness_probe {
            http_get {
              path = each.value.probe
              port = each.value.port
            }
            initial_delay_seconds = 20
            period_seconds        = 10
          }
          liveness_probe {
            http_get {
              path = each.value.probe
              port = each.value.port
            }
            initial_delay_seconds = 40
            period_seconds        = 20
          }
          resources {
            requests = { cpu = each.value.cpu, memory = each.value.mem_req }
            limits   = { memory = each.value.mem_lim }
          }
        }
      }
    }
  }
}

resource "kubernetes_service_v1" "svc" {
  for_each = local.services

  metadata {
    name      = each.key
    namespace = kubernetes_namespace_v1.vkp.metadata[0].name
    labels    = { app = each.key }
  }
  spec {
    selector = { app = each.key }
    port {
      port        = each.value.port
      target_port = each.value.port
    }
  }
}
