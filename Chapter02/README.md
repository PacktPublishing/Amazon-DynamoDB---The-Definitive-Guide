# 2. The AWS Management Console, and SDKs

## Getting familiar with the AWS SDK

[Installing the latest version of official AWS SDK for Python (Boto3)](#installing-the-latest-version-of-official-aws-sdk-for-python-boto3)
- [Using the AWS SDK](#using-the-aws-sdk)
    - [Python code to run `Scan` API on table with name `DefinitiveGuide01`](#python-code-to-run-scan-api-on-table-with-name-definitiveguide01)
    - [Python code to run `Query` API on table with name `DefinitiveGuide01`](#python-code-to-run-query-api-on-table-with-name-definitiveguide01)
    - [Python code to run `GetItem` API on table with name `DefinitiveGuide01`](#python-code-to-run-getitem-api-on-table-with-name-definitiveguide01)
  - [Using AWS Lambda and installing DynamoDB local](#using-aws-lambda-and-installing-dynamodb-local)
    - [AWS Lambda function code in Python for DynamoDB `Scan`](#aws-lambda-function-code-in-python-for-dynamodb-scan)
    - [AWS Lambda function code in Python for DynamoDB `Query`](#aws-lambda-function-code-in-python-for-dynamodb-query)
    - [Initializing Boto3 DynamoDB client for DynamoDB local](#initializing-boto3-dynamodb-client-for-dynamodb-local)

#### Installing the latest version of official AWS SDK for Python (Boto3)

```shell
pip install boto3
```

### Using the AWS SDK

#### Python code to run `Scan` API on table with name `DefinitiveGuide01`

```python
import boto3

# Initialize a DynamoDB resource
dynamodb = boto3.resource('dynamodb')  

# Specify the table
table = dynamodb.Table('DefinitiveGuide01')  

# Scan the table
response = table.scan()

# Extract the items from the response
items = response['Items']

# Print the retrieved items
print(items)
```

#### Python code to run `Query` API on table with name `DefinitiveGuide01`

```python
import boto3  

# Initialize a DynamoDB resource
dynamodb = boto3.resource('dynamodb')  

# Specify the table
table = dynamodb.Table('DefinitiveGuide01')  

# Query the table
response = table.query(
    KeyConditionExpression='id = :catnum',  
    ExpressionAttributeValues={
        ':catnum': 'ADJ004'
        }
    )  

# Extract the items from the response
items = response['Items']  

# Print the retrieved items
print(items) 
```

#### Python code to run `GetItem` API on table with name `DefinitiveGuide01`

```python
import boto3  

# Initialize a DynamoDB resource
dynamodb = boto3.resource('dynamodb')  

# Specify the table
table = dynamodb.Table('DefinitiveGuide01')

# Retrieve an item from the table
response = table.get_item(
    Key={
        'id': 'ADJ004'
    }
)

# Extract the item from the response
items = response['Item']

# Print the retrieved item
print(items)
```

### Using AWS Lambda and installing DynamoDB local

#### AWS Lambda function code in Python for DynamoDB `Scan`

```python
import boto3

# Initialize a DynamoDB resource
dynamodb = boto3.resource('dynamodb')  

# Specify the table
table = dynamodb.Table('DefinitiveGuide01')

def lambda_handler(event, context):
    # Scan the table
    response = table.scan(
        ReturnConsumedCapacity='TOTAL'
    )
    # Extract the items from the response
    items = response['Items']

    # Return the response with a status code and body
    return {
        'statusCode': 200,
        'body': items
    }
```

#### AWS Lambda function code in Python for DynamoDB `Query`

```python
import boto3

# Initialize a DynamoDB resource
dynamodb = boto3.resource('dynamodb')  

# Specify the table
table = dynamodb.Table('DefinitiveGuide01')

def lambda_handler(event, context):
    # Query the table
    response = table.query(
        KeyConditionExpression='id = :catnum',
        ExpressionAttributeValues={
            ':catnum': 'ADJ004'
        }
    )
    
    # Extract the items from the response
    items = response['Items']

    # Return the response with a status code and body
    return {
        'statusCode': 200,
        'body': items
    }
```

#### Initializing Boto3 DynamoDB client for DynamoDB local

```python
import boto3

# Initialize a DynamoDB resource with a specified endpoint URL
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url='https://localhost:8000'
)
```

