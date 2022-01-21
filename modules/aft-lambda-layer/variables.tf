variable "lambda_layer_name" {
  type = string
  validation {
    condition     = can(regex("^[a-zA-Z0-9\\-]+$", var.lambda_layer_name))
    error_message = "Layer name must contain only alphanumeric characters and hyphens."
  }
}

variable "aft_tf_aws_customizations_module_url_ssm_path" {
  type = string
}

variable "aft_tf_aws_customizations_module_git_ref_ssm_path" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "lambda_layer_codebuild_delay" {
  type = string
}

variable "lambda_layer_python_version" {
  type = string
}

variable "s3_bucket_name" {
  type = string
}

variable "aft_kms_key_arn" {
  type = string
}

variable "aft_vpc_id" {
  type = string
}

variable "aft_vpc_private_subnets" {
  type = list(string)
}

variable "aft_vpc_default_sg" {
  type = list(string)
}
variable "aft_version" {
  type = string
}
