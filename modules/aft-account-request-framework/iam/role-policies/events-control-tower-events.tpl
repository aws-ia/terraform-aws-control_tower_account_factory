{
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "events:PutEvents"
        ],
        "Resource" : [
          "${aws_cloudwatch_event_bus_from-ct-management_arn}"
        ]
      }
    ]
}
