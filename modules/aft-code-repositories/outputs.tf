output "codestar_connection_arn" {
  value = lookup(local.connection_arn, var.vcs_provider)
}