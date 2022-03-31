provider "aws" {
  alias  = "aft_netops"
  region = "us-east-1"
}

######################
## NetOps Permission set
######################

resource "aws_ssoadmin_permission_set" "NetOps" {
  name         = "NetOps"
  instance_arn = "arn:aws:sso:::instance/ssoins-7223dc3f7c2fa8bd"
  description  = "Grants full access permissions to AWS services and actions required to set up and configure AWS network resources."
}

resource "aws_ssoadmin_managed_policy_attachment" "NetOps-attachment" {
  instance_arn       = "arn:aws:sso:::instance/ssoins-7223dc3f7c2fa8bd"
  managed_policy_arn = "arn:aws:iam::aws:policy/job-function/NetworkAdministrator"
  permission_set_arn = aws_ssoadmin_permission_set.NetOps.arn
}


######################
## DataEngineer Permission set
######################

resource "aws_ssoadmin_permission_set" "DataEngineer" {
  name         = "DataEngineer"
  instance_arn = "arn:aws:sso:::instance/ssoins-7223dc3f7c2fa8bd"
  description  =  "Grants permissions to AWS data analytics services."
}

resource "aws_ssoadmin_managed_policy_attachment" "DataEngineer-attachment" {
  instance_arn       = "arn:aws:sso:::instance/ssoins-7223dc3f7c2fa8bd"
  managed_policy_arn = "arn:aws:iam::aws:policy/job-function/DataScientist"
  permission_set_arn = aws_ssoadmin_permission_set.DataEngineer.arn
}


######################
## DatabaseAdministrator Permission set
######################

resource "aws_ssoadmin_permission_set" "DatabaseAdministrator" {
  name         = "DatabaseAdministrator"
  instance_arn = "arn:aws:sso:::instance/ssoins-7223dc3f7c2fa8bd"
  description = "Grants full access permissions to AWS services and actions required to set up and configure AWS database services."
}

resource "aws_ssoadmin_managed_policy_attachment" "DatabaseAdministrator-attachment" {
  instance_arn       = "arn:aws:sso:::instance/ssoins-7223dc3f7c2fa8bd"
  managed_policy_arn = "arn:aws:iam::aws:policy/job-function/DatabaseAdministrator"
  permission_set_arn = aws_ssoadmin_permission_set.DatabaseAdministrator.arn
}


######################
## PowerUserAccess Permission set
######################

resource "aws_ssoadmin_permission_set" "PowerUserAccess" {
  name         = "PowerUserAccess"
  instance_arn = "arn:aws:sso:::instance/ssoins-7223dc3f7c2fa8bd"
  description = "Provides full access to AWS services and resources, but does not allow management of Users and groups."
}

resource "aws_ssoadmin_managed_policy_attachment" "PowerUserAccess-attachment" {
  instance_arn       = "arn:aws:sso:::instance/ssoins-7223dc3f7c2fa8bd"
  managed_policy_arn = "arn:aws:iam::aws:policy/PowerUserAccess"
  permission_set_arn = aws_ssoadmin_permission_set.PowerUserAccess.arn
}


######################
## SecurityAudit Permission set
######################

resource "aws_ssoadmin_permission_set" "SecurityAudit" {
  name         = "SecurityAudit"
  instance_arn = "arn:aws:sso:::instance/ssoins-7223dc3f7c2fa8bd"
  description = "Provides full access to AWS services and resources, but does not allow management of Users and groups."
}

resource "aws_ssoadmin_managed_policy_attachment" "SecurityAudit-attachment" {
  instance_arn       = "arn:aws:sso:::instance/ssoins-7223dc3f7c2fa8bd"
  managed_policy_arn = "arn:aws:iam::aws:policy/SecurityAudit"
  permission_set_arn = aws_ssoadmin_permission_set.SecurityAudit.arn
}


######################
## ViewOnlyAccess Permission set
######################

resource "aws_ssoadmin_permission_set" "ViewOnlyAccess" {
  name         = "ViewOnlyAccess"
  instance_arn = "arn:aws:sso:::instance/ssoins-7223dc3f7c2fa8bd"
  description = "This policy grants permissions to view resources and basic metadata across all AWS services."
}

resource "aws_ssoadmin_managed_policy_attachment" "ViewOnlyAccess-attachment" {
  instance_arn       = "arn:aws:sso:::instance/ssoins-7223dc3f7c2fa8bd"
  managed_policy_arn = "arn:aws:iam::aws:policy/job-function/ViewOnlyAccess"
  permission_set_arn = aws_ssoadmin_permission_set.ViewOnlyAccess.arn
}


######################
## SystemAdministrator Permission set
######################

resource "aws_ssoadmin_permission_set" "SystemAdministrator" {
  name         = "SystemAdministrator"
  instance_arn = "arn:aws:sso:::instance/ssoins-7223dc3f7c2fa8bd"
  description = "Grants full access permissions necessary for resources required for application and development operations.."
}

resource "aws_ssoadmin_managed_policy_attachment" "SystemAdministrator-attachment" {
  instance_arn       = "arn:aws:sso:::instance/ssoins-7223dc3f7c2fa8bd"
  managed_policy_arn = "arn:aws:iam::aws:policy/job-function/SystemAdministrator"
  permission_set_arn = aws_ssoadmin_permission_set.SystemAdministrator.arn
}


