output "provisioning_framework_archive_path" {
  value = data.archive_file.provisioning_framework.output_path
}

output "provisioning_framework_archive_hash" {
  value = data.archive_file.provisioning_framework.output_base64sha256
}

output "request_framework_archive_path" {
  value = data.archive_file.request_framework.output_path
}

output "request_framework_archive_hash" {
  value = data.archive_file.request_framework.output_base64sha256
}

output "customizations_archive_path" {
  value = data.archive_file.customizations.output_path
}

output "customizations_archive_hash" {
  value = data.archive_file.customizations.output_base64sha256
}

output "feature_options_archive_path" {
  value = data.archive_file.feature_options.output_path
}

output "feature_options_archive_hash" {
  value = data.archive_file.feature_options.output_base64sha256
}
