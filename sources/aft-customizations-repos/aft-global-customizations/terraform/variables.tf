variable "tags" {
  default = {
    Owner = "kms-test"
  }
}

variable "user_policy" {
  default = ""
}

variable "username" {
  default = "GFT"
}

 variable "aws_region" {
   default = "us-east-1"
 }
 
 variable "replica_region" {
   default = "us-east-2"
 }
 
 variable "replica_region2" {
   default = "eu-west-2"
 }
 
