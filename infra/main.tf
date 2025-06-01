provider "aws" {
  region = "us-east-1"
}

resource "aws_iam_role" "lambda_role" {
  name = "lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Effect = "Allow"
        Sid    = ""
      }
    ]
  })
}

resource "aws_iam_policy" "dynamodb_policy" {
  name        = "dynamodb_access_policy"
  description = "Policy to allow access to DynamoDB"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:UpdateItem",
          "dynamodb:Scan"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_dynamodb" {
  policy_arn = aws_iam_policy.dynamodb_policy.arn
  role       = aws_iam_role.lambda_role.name
}

resource "aws_lambda_function" "cadastro_pessoa" {
  function_name = var.lambda_function_name
  handler       = "bootstrap"
  runtime       = "provided.al2"
  role          = aws_iam_role.lambda_role.arn
  filename      = "../app/lambda_cadastro_pessoa.zip"
  source_code_hash = filebase64sha256("../app/lambda_cadastro_pessoa.zip")

  environment {
    variables = {
      sistemavantable = var.dynamodb_table_name
    }
  }
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${var.lambda_function_name}"
  retention_in_days = 5
}

resource "aws_dynamodb_table" "sistemavan_table" {
  name         = var.dynamodb_table_name
  billing_mode = "PAY_PER_REQUEST"

  attribute {
    name = "data"
    type = "S"
  }

  attribute {
    name = "identificador"
    type = "S"
  }

  hash_key  = "data"
  range_key = "identificador"
}

resource "aws_api_gateway_rest_api" "cadastro_api" {
  name        = "cadastro-api"
  description = "API Gateway para cadastro de pessoa"
}

resource "aws_api_gateway_resource" "cadastro_resource" {
  rest_api_id = aws_api_gateway_rest_api.cadastro_api.id
  parent_id   = aws_api_gateway_rest_api.cadastro_api.root_resource_id
  path_part   = "cadastro"
}

resource "aws_api_gateway_method" "cadastro_post" {
  rest_api_id   = aws_api_gateway_rest_api.cadastro_api.id
  resource_id   = aws_api_gateway_resource.cadastro_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "cadastro_lambda" {
  rest_api_id = aws_api_gateway_rest_api.cadastro_api.id
  resource_id = aws_api_gateway_resource.cadastro_resource.id
  http_method = aws_api_gateway_method.cadastro_post.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.cadastro_pessoa.invoke_arn
}

resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cadastro_pessoa.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.cadastro_api.execution_arn}/*/*"
}

resource "aws_api_gateway_deployment" "cadastro_deployment" {
  depends_on = [
    aws_api_gateway_integration.cadastro_lambda,
    aws_api_gateway_integration.cadastro_lambda_get,
    aws_api_gateway_integration.cadastro_lambda_put,
    aws_api_gateway_integration.cadastro_options
  ]
  rest_api_id = aws_api_gateway_rest_api.cadastro_api.id
}

resource "aws_api_gateway_stage" "cadastro_stage" {
  stage_name    = "prod"
  rest_api_id   = aws_api_gateway_rest_api.cadastro_api.id
  deployment_id = aws_api_gateway_deployment.cadastro_deployment.id
}

resource "aws_api_gateway_method_response" "cadastro_post_200" {
  rest_api_id = aws_api_gateway_rest_api.cadastro_api.id
  resource_id = aws_api_gateway_resource.cadastro_resource.id
  http_method = aws_api_gateway_method.cadastro_post.http_method
  status_code = "200"

  response_models = {
    "application/json" = "Empty"
  }

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
  }
}

resource "aws_api_gateway_integration_response" "cadastro_post_200" {
  rest_api_id = aws_api_gateway_rest_api.cadastro_api.id
  resource_id = aws_api_gateway_resource.cadastro_resource.id
  http_method = aws_api_gateway_method.cadastro_post.http_method
  status_code = aws_api_gateway_method_response.cadastro_post_200.status_code
  selection_pattern = ""

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type'"
    "method.response.header.Access-Control-Allow-Methods" = "'OPTIONS,POST'"
  }
}

resource "aws_api_gateway_method" "cadastro_options" {
  rest_api_id   = aws_api_gateway_rest_api.cadastro_api.id
  resource_id   = aws_api_gateway_resource.cadastro_resource.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "cadastro_options" {
  rest_api_id = aws_api_gateway_rest_api.cadastro_api.id
  resource_id = aws_api_gateway_resource.cadastro_resource.id
  http_method = aws_api_gateway_method.cadastro_options.http_method

  type = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }

  integration_http_method = "OPTIONS"
}

resource "aws_api_gateway_method_response" "cadastro_options_200" {
  rest_api_id = aws_api_gateway_rest_api.cadastro_api.id
  resource_id = aws_api_gateway_resource.cadastro_resource.id
  http_method = aws_api_gateway_method.cadastro_options.http_method
  status_code = "200"

  response_models = {
    "application/json" = "Empty"
  }

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
  }
}

resource "aws_api_gateway_integration_response" "cadastro_options_200" {
  depends_on = [aws_api_gateway_integration.cadastro_options]
  rest_api_id = aws_api_gateway_rest_api.cadastro_api.id
  resource_id = aws_api_gateway_resource.cadastro_resource.id
  http_method = aws_api_gateway_method.cadastro_options.http_method
  status_code = aws_api_gateway_method_response.cadastro_options_200.status_code
  selection_pattern = ""

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization,X-Requested-With'"
    "method.response.header.Access-Control-Allow-Methods" = "'OPTIONS,POST,PUT,GET'"
  }
}

resource "aws_api_gateway_method" "cadastro_get" {
  rest_api_id   = aws_api_gateway_rest_api.cadastro_api.id
  resource_id   = aws_api_gateway_resource.cadastro_resource.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "cadastro_lambda_get" {
  rest_api_id = aws_api_gateway_rest_api.cadastro_api.id
  resource_id = aws_api_gateway_resource.cadastro_resource.id
  http_method = aws_api_gateway_method.cadastro_get.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.cadastro_pessoa.invoke_arn
}

resource "aws_api_gateway_method_response" "cadastro_get_200" {
  rest_api_id = aws_api_gateway_rest_api.cadastro_api.id
  resource_id = aws_api_gateway_resource.cadastro_resource.id
  http_method = aws_api_gateway_method.cadastro_get.http_method
  status_code = "200"

  response_models = {
    "application/json" = "Empty"
  }

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
  }
}

resource "aws_api_gateway_integration_response" "cadastro_get_200" {
  rest_api_id = aws_api_gateway_rest_api.cadastro_api.id
  resource_id = aws_api_gateway_resource.cadastro_resource.id
  http_method = aws_api_gateway_method.cadastro_get.http_method
  status_code = aws_api_gateway_method_response.cadastro_get_200.status_code
  selection_pattern = ""

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type'"
    "method.response.header.Access-Control-Allow-Methods" = "'OPTIONS,POST,PUT,GET'"
  }
}

resource "aws_api_gateway_method" "cadastro_put" {
  rest_api_id   = aws_api_gateway_rest_api.cadastro_api.id
  resource_id   = aws_api_gateway_resource.cadastro_resource.id
  http_method   = "PUT"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "cadastro_lambda_put" {
  rest_api_id = aws_api_gateway_rest_api.cadastro_api.id
  resource_id = aws_api_gateway_resource.cadastro_resource.id
  http_method = aws_api_gateway_method.cadastro_put.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.cadastro_pessoa.invoke_arn
}

resource "aws_api_gateway_method_response" "cadastro_put_200" {
  rest_api_id = aws_api_gateway_rest_api.cadastro_api.id
  resource_id = aws_api_gateway_resource.cadastro_resource.id
  http_method = aws_api_gateway_method.cadastro_put.http_method
  status_code = "200"

  response_models = {
    "application/json" = "Empty"
  }

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
  }
}

resource "aws_api_gateway_integration_response" "cadastro_put_200" {
  depends_on = [aws_api_gateway_integration.cadastro_lambda_put]
  rest_api_id = aws_api_gateway_rest_api.cadastro_api.id
  resource_id = aws_api_gateway_resource.cadastro_resource.id
  http_method = aws_api_gateway_method.cadastro_put.http_method
  status_code = aws_api_gateway_method_response.cadastro_put_200.status_code
  selection_pattern = ""

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type'"
    "method.response.header.Access-Control-Allow-Methods" = "'OPTIONS,POST,GET,PUT'"
  }
}