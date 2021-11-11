{
"Version": "2012-10-17",
"Statement": [
{
"Action": ["sts:AssumeRole"],
"Effect": "allow",
"Principal": {
"Service": ["backup.amazonaws.com"]
}
}
]
}