variable "kubeconfig" {
  description = "Path to the kubeconfig for the target cluster."
  type        = string
  default     = "~/.kube/config"
}

variable "kube_context" {
  description = "kubeconfig context to use (empty = current-context)."
  type        = string
  default     = ""
}

variable "namespace" {
  description = "Namespace for all VKP workloads."
  type        = string
  default     = "vkp"
}

variable "image_registry" {
  description = "Container registry + org prefix for the vkp-* images."
  type        = string
  default     = "ghcr.io/javakishore-veleti"
}

variable "image_tag" {
  description = "Image tag to deploy (CI typically sets the git SHA)."
  type        = string
  default     = "dev"
}

# --- Secrets (provide via a tfvars file or TF_VAR_*; never commit real values) ---
variable "jwt_secret" {
  description = "HS256 JWT secret — MUST be identical across all services."
  type        = string
  sensitive   = true
  default     = "change-me-dev-secret-please-override-in-prod-0123456789"
}

variable "session_secret" {
  description = "Base64 of a 32-byte AES key for vkp-session-security (blank = ephemeral)."
  type        = string
  sensitive   = true
  default     = ""
}

variable "db_password" {
  description = "Postgres password shared by the services."
  type        = string
  sensitive   = true
  default     = "vkp"
}

variable "openai_api_key" {
  type      = string
  sensitive = true
  default   = ""
}

variable "groq_api_key" {
  type      = string
  sensitive = true
  default   = ""
}
