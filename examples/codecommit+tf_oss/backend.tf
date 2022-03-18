terraform {
    backend "s3" {
        bucket = "bucket_name"
        region = "us-east-1"
        key    = "terraform.state"
    }
}