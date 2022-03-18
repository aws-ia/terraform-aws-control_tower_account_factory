variable "trusted_entity_type" {
  default = "AWS"
}

variable "trusted_entity" {
  default = "947117813606"
}


## Creation of NetOps role ##
resource "aws_iam_role" "netops_role" {
  name = "netops_role"
  assume_role_policy = templatefile("${path.module}/trust_policy.tpl",
    {
      trusted_entity_type = var.trusted_entity_type
      trusted_entity      = var.trusted_entity
    }
  )

  managed_policy_arns = ["arn:aws:iam::aws:policy/job-function/NetworkAdministrator"]
}



## Creation of DataEngineer role ##
resource "aws_iam_role" "data_engineer_role" {
  name = "data_engineer_role"
  assume_role_policy = templatefile("${path.module}/trust_policy.tpl",
    {
      trusted_entity_type = var.trusted_entity_type
      trusted_entity      = var.trusted_entity
    }
  )

  managed_policy_arns = ["arn:aws:iam::aws:policy/job-function/DataScientist"]
}



## Creation of SysOps role ##
resource "aws_iam_role" "sysops_role" {
  name = "sysops_role"
  assume_role_policy = templatefile("${path.module}/trust_policy.tpl",
    {
      trusted_entity_type = var.trusted_entity_type
      trusted_entity      = var.trusted_entity
    }
  )

  managed_policy_arns = ["arn:aws:iam::aws:policy/job-function/SystemAdministrator"]
}

## Creation of SSM-Session role ##
resource "aws_iam_role" "ssm_session_role" {
  name = "ssm_session_role"
  assume_role_policy = templatefile("${path.module}/trust_policy.tpl",
    {
      trusted_entity_type = var.trusted_entity_type
      trusted_entity      = var.trusted_entity
    }
  )

  managed_policy_arns = ["arn:aws:iam::aws:policy/AmazonSSMFullAccess"]
}

## Creation of DB-Admin role ##
resource "aws_iam_role" "db_admin_role" {
  name = "db_admin_role"
  assume_role_policy = templatefile("${path.module}/trust_policy.tpl",
    {
      trusted_entity_type = var.trusted_entity_type
      trusted_entity      = var.trusted_entity
    }
  )

  managed_policy_arns = ["arn:aws:iam::aws:policy/job-function/DatabaseAdministrator"]
}

## Creation of CodePipeline-Ops role ##
resource "aws_iam_role" "codepipeline_ops_role" {
  name = "codepipeline_ops_role"
  assume_role_policy = templatefile("${path.module}/trust_policy.tpl",
    {
      trusted_entity_type = var.trusted_entity_type
      trusted_entity      = var.trusted_entity
    }
  )

  managed_policy_arns = ["arn:aws:iam::aws:policy/AWSCodePipelineFullAccess"]
}