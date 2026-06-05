output "namespace" {
  description = "Namespace all VKP workloads were deployed into."
  value       = kubernetes_namespace_v1.vkp.metadata[0].name
}

output "services" {
  description = "Deployed service -> in-cluster DNS:port."
  value       = { for name, s in local.services : name => "${name}.${var.namespace}.svc.cluster.local:${s.port}" }
}

output "image_refs" {
  description = "Resolved image reference per service."
  value       = { for name, s in local.services : name => s.image_ref }
}
