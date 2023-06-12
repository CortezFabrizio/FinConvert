
resource "aws_sns_topic" "finconvert_sns" {
  name = "user-updates-topic"
}

resource "aws_sqs_queue" "insert_table_queue" {
  name                      = "TickerQueue"
  max_message_size          = 2048
  message_retention_seconds = 345600

}

resource "aws_sns_topic_subscription" "user_updates_sqs_target" {
  topic_arn = aws_sns_topic.finconvert_sns.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.insert_table_queue.arn
}


resource "aws_lambda_function" "lambda_insert_table" {

  filename      = "${var.lambda_path}"
  function_name = "lambda_insert_table"
  role          = "${var.lambda_arn_role}"
  handler       = "lambda_function.insert_table"
  runtime = "python3.10"

}


resource "aws_lambda_event_source_mapping" "event_source_mapping" {
  event_source_arn = aws_sqs_queue.insert_table_queue.arn
  enabled          = true
  function_name    = aws_lambda_function.lambda_insert_table.arn
  batch_size       = 1
}