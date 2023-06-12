provider "aws" {
  region = "us-west-2"  
}

resource "aws_ecs_cluster" "fin_cluster" {
  name = "finconvert_fastapi"
}


resource "aws_iam_instance_profile" "test_profile" {
  name = "test_profile"
  role = aws_iam_role.ecs_Instance_role.name
}


resource "aws_launch_configuration" "ec2_launch_config" {
  name                 = "ec2-launch-config"
  image_id             = "ami-0be4bf0879ccaadb3"  
  instance_type        = "t2.micro"     
  key_name             = "fincon"  
  associate_public_ip_address = true

  user_data = templatefile("${path.module}/startup.sh",{
    CLUSTER_NAME=aws_ecs_cluster.fin_cluster.name
  })

  security_groups      = [aws_security_group.ec2_firewall.id]
  iam_instance_profile = aws_iam_instance_profile.test_profile.name

}


resource "aws_autoscaling_group" "finconvert_asg" {
    tag {
    key                 = "AmazonECSManaged"
    value               = true
    propagate_at_launch = true
  }

  name                = "finconvert-autoscaling-group"
  launch_configuration = aws_launch_configuration.ec2_launch_config.name
  min_size            = 1
  max_size            = 1
  desired_capacity    = 1
}




resource "aws_ecs_task_definition" "fastapi_task_definition" {
  family                   = "fastapi_task"
  execution_role_arn       = "${var.fast_api_task_role}"
  network_mode             = "bridge"
  task_role_arn            = "${var.fast_api_task_role}"
  container_definitions    =  file("${path.module}/json_confs/fastAPI_def.json")
}


resource "aws_ecs_service" "fast_api_service" {
  name           = "fast_api_service"
  cluster        = aws_ecs_cluster.fin_cluster.id
  task_definition = aws_ecs_task_definition.fastapi_task_definition.arn
  desired_count  = 1
  launch_type    = "EC2"
}




resource "aws_ecs_task_definition" "nginx_task_definition" {
  family                   = "nginx_task"
  execution_role_arn       = "${var.nginx_task_role}"
  network_mode             = "bridge"
  task_role_arn            = "${var.nginx_task_role}"
  
  container_definitions    =  file("${path.module}/json_confs/nginx_def.json")
}


resource "aws_ecs_service" "nginx_service" {
  name           = "nginx"
  cluster        = aws_ecs_cluster.fin_cluster.id
  task_definition = aws_ecs_task_definition.nginx_task_definition.arn
  desired_count  = 1
  launch_type    = "EC2"
}