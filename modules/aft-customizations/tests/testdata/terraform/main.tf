resource "aws_ssm_parameter" "hello_world" {
  name  = "/aft-global-customizations/terraform/unittests/hello-world"
  type  = "String"
  value = "Hello World!"
}
