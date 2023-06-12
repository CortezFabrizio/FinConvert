resource "aws_dynamodb_table" "financials_db" {
  name             = "fabri_app" 
  billing_mode     = "PROVISIONED"
  read_capacity    = 1
  write_capacity   = 1 
  hash_key         = "ticker"
  
  attribute {
    name = "ticker"
    type = "S"
  }

}