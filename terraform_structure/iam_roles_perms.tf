resource "aws_iam_role" "ecs_Instance_role" {
  name = "ecs_Instace_role"

  assume_role_policy = jsonencode({
    "Version": "2008-10-17",
    "Statement": [
        {
            "Sid": "",
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
})

  managed_policy_arns = [aws_iam_policy.policy_one.arn]


}


resource "aws_iam_policy" "policy_one" {
  name = "policy-618033"

  policy =file("${path.module}/json_confs/ec2_ecs_role.json")
}


