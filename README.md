# Instrumenting an AWS Bedrock Lambda function for Datadog LLM Obs (Python)
In this lab, we will create a very simple AWS Bedrock based chatbot running in an AWS Lambda function, in Python. Then we will instrument the Lambda function with Datadog LLM Obs to get the LLM chain traces sent to Datadog.
First we will create the AWS Lambda function from scratch, then we will instrument it with the Datadog Lambda extension (APM tracing library for Lambda functions) + LLM Obs environment variables.
