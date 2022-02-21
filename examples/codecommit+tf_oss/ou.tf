# pulling the organization data from AWS
data "aws_organizations_organization" "root" {}

# Creating OUs for the different purposes (Network, services...)
resource "aws_organizations_organizational_unit" "ou" {
  name      = "OUtesting" # name of the OU to create
  parent_id = aws_organizations_organization.root.roots[0].id
}