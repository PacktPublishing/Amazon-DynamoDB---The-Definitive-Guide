# 15. Enhanced Analytical Patterns

- [AWS Lambda and AWS Step Functions](#aws-lambda-and-aws-step-functions)
  * [GenerateShuffledNumbers function](#generateshufflednumbers-function)
  * [ProcessNumber function](#processnumber-function)
- [AWS Lambda and Amazon Simple Queue Service (SQS)](#aws-lambda-and-amazon-simple-queue-service--sqs-)
  * [SQSTableScanner function](#sqstablescanner-function)
- [AWS Glue-based examples](#aws-glue-based-examples)
  * [AWS Glue read/write examples](#aws-glue-read-write-examples)
  * [High-level walkthrough of parallelizing Boto3 code in AWS Glue](#high-level-walkthrough-of-parallelizing-boto3-code-in-aws-glue)
  * [Rate-limiting AWS Glue script using Token bucket algorithm and ReturnConsumedCapacity](#rate-limiting-aws-glue-script-using-token-bucket-algorithm-and-returnconsumedcapacity)
  * [Full script to parallelize Boto3-based code in AWS Glue](#full-script-to-parallelize-boto3-based-code-in-aws-glue)

### AWS Lambda and AWS Step Functions

#### GenerateShuffledNumbers function
[lambda_generate_shuffled_numbers.py](lambda_generate_shuffled_numbers.py)

#### ProcessNumber function
[lambda_process_number.py](lambda_process_number.py)

### AWS Lambda and Amazon Simple Queue Service (SQS)

#### SQSTableScanner function
[lambda_sqs_table_scanner.py](lambda_sqs_table_scanner.py)

### AWS Glue-based examples

#### AWS Glue read/write examples
```python
# Reading from DynamoDB table using parallel Scan
dyf = glue_context.create_dynamic_frame.from_options(
    connection_type="dynamodb",
    connection_options={
        "dynamodb.input.tableName": test_source,
        "dynamodb.throughput.read.percent": "1.0"  # Utilize 100% of provisioned read capacity
    }
)

# Writing into DynamoDB table using BatchWriteItem
glue_context.write_dynamic_frame_from_options(
    frame=dyf,
    connection_type="dynamodb",
    connection_options={
        "dynamodb.output.tableName": test_sink,
        "dynamodb.throughput.write.percent": "1.0"  # Utilize 100% of provisioned write capacity
    }
)
```

#### High-level walkthrough of parallelizing Boto3 code in AWS Glue

```python
# Read from S3 export
df = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={
        "compressionType": "gzip",
        "paths": ['s3://path/to/exported/data/']
    },
    format="json",
    transformation_ctx="df"
).toDF()  # Convert the dynamic frame to a Spark DataFrame


def process_item_update(boto3_table, item):
    """
    Process an item update in DynamoDB using the UpdateItem API.

    Args:
        boto3_table (boto3.Table): The DynamoDB table resource.
        item (dict): The item to be updated in the DynamoDB table.

    Returns:
        dict: The response from the update_item call.
    """
    try:
        # Issue update_item call
        update_response = boto3_table.update_item(
            Key={'pk': item.get('pk'), 'sk': item.get('sk')},
            ConditionExpression="attribute_not_exists(NewAttribute)",
            UpdateExpression="SET NewAttribute = :new_attr_val",
            ExpressionAttributeValues={':new_attr_val': 'NewAttributeValue'},
            ReturnConsumedCapacity='INDEXES'
        )
        return update_response
    except Exception as e:
        # Handle throttles and condition check failures
        print(f"Error updating item: {e}")
        raise


def execution_for_each_spark_partition(partitionData):
    """
    Execute update operations for each partition of Spark data.

    Args:
        partitionData (iterable): The data partition to be processed.
    """
    # Initialize DynamoDB client on each Glue executor
    ddbclient = boto3.resource('dynamodb', region_name='eu-west-1', config=Config(
        region_name='eu-west-1',
        max_pool_connections=100,
        retries={'max_attempts': 10, 'mode': 'adaptive'}
    ))
    table = ddbclient.Table('TABLE_NAME')  # Replace 'TABLE_NAME' with your DynamoDB table name

    for item in partitionData:
        response = process_item_update(table, item)
        # Use response and output of ReturnConsumedCapacity to rate-limit here

# Convert to Spark RDD and parallelize processing across partitions
df.rdd.foreachPartition(execution_for_each_spark_partition)
```

#### Rate-limiting AWS Glue script using Token bucket algorithm and ReturnConsumedCapacity

```python
# Get job infrastructure details to parallelize processing efficiently
TASKS_PER_EXECUTOR = int(spark.sparkContext.getConf().get("spark.executor.cores"))
NUM_EXECUTORS = int(spark.sparkContext.getConf().get("spark.executor.instances"))

print("#### Tasks per executor: %d | Num executors: %d" % (TASKS_PER_EXECUTOR, NUM_EXECUTORS))

WRITE_THROUGHPUT_PERCENT = "1.0"
SPLITS_STR = str(NUM_EXECUTORS * TASKS_PER_EXECUTOR)

# Use infrastructure details and WRITE_THROUGHPUT_PERCENT to compute max WCU per Spark partition
# MAX_WCU_PER_TASK obtained will be used to rate-limit on individual Spark partition/Glue worker level

if table.billing_mode_summary is not None and table.billing_mode_summary['BillingMode'] == 'PAY_PER_REQUEST':
    TOTAL_WCU_TARGET = float(WRITE_THROUGHPUT_PERCENT) * 40000
else:
    TOTAL_WCU_TARGET = float(WRITE_THROUGHPUT_PERCENT) * table.provisioned_throughput['WriteCapacityUnits']

MAX_WCU_PER_TASK = float(TOTAL_WCU_TARGET) / (TASKS_PER_EXECUTOR * NUM_EXECUTORS)

print("#### Max WCU per task: %f | Tasks per executor: %d | Num executors: %d | Splits: %s" % (
    MAX_WCU_PER_TASK, TASKS_PER_EXECUTOR, NUM_EXECUTORS, SPLITS_STR))


def process_item_update(boto3_table, item):
    """
    Process an item update in DynamoDB using the UpdateItem API.

    Args:
        boto3_table (boto3.Table): The DynamoDB table resource.
        item (dict): The item to be updated in the DynamoDB table.

    Returns:
        dict: The response from the update_item call, or None if an exception occurs.
    """
    update_response = None
    try:
        # Issue update_item call (example code)
        # update_response = boto3_table.update_item(
        #     Key={'pk': item.get('pk'), 'sk': item.get('sk')},
        #     ConditionExpression="attribute_not_exists(NewAttribute)",
        #     UpdateExpression="SET NewAttribute = :new_attr_val",
        #     ExpressionAttributeValues={':new_attr_val': 'NewAttributeValue'},
        #     ReturnConsumedCapacity='INDEXES'
        # )
        pass

    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            # Condition check failed, do nothing
            pass
        elif e.response['Error']['Code'] == 'ProvisionedThroughputExceededException':
            # Request throttled, retry the update
            update_response = process_item_update(boto3_table, item)

    return update_response


def execution_for_each_spark_partition(partitionData):
    """
    Execute update operations for each partition of Spark data.

    Args:
        partitionData (iterable): The data partition to be processed.
    """
    global MAX_WCU_PER_TASK

    # Initialize boto3 client and table resource
    ddbclient = boto3.resource('dynamodb', region_name='eu-west-1', config=Config(
        region_name='eu-west-1',
        max_pool_connections=100,
        retries={'max_attempts': 10, 'mode': 'adaptive'}
    ))
    table = ddbclient.Table('TABLE_NAME')  # Replace 'TABLE_NAME' with your DynamoDB table name

    rate = MAX_WCU_PER_TASK  # WCU rate limit
    per = 1  # Time unit in seconds
    allowance = rate  # WCU allowance
    last_check = time.time()  # Current time in seconds

    task_item_count = 0  # Counter to log progress

    for item in partitionData:
        current = time.time()
        time_passed = current - last_check
        last_check = current
        allowance += time_passed * (rate / per)

        if allowance > rate:
            allowance = rate

        if allowance < 1.0:  # No tokens remaining
            delta_time = float(time.time() + 1) - time.time()
            if delta_time > 0.0:
                time.sleep(delta_time)

        response = process_item_update(table, item)
        task_item_count += 1

        # Using consumed capacity per request to rate-limit
        if response is not None:
            total_consumed_capacity = response['ConsumedCapacity']
            tokens_to_deduct = total_consumed_capacity['Table']['CapacityUnits']

            # Deduct additional tokens for rate limiting if LSI WCU is also consumed
            if 'LocalSecondaryIndexes' in total_consumed_capacity:
                lsi_key_name = list(total_consumed_capacity['LocalSecondaryIndexes'].keys())
                lsi_name = lsi_key_name[0]
                tokens_to_deduct += total_consumed_capacity['LocalSecondaryIndexes'][lsi_name]['CapacityUnits']

            allowance -= tokens_to_deduct
        else:
            # Response is None due to ConditionCheckFailedException
            allowance -= 1

    print("#### Items processed for current task: %d" % task_item_count)
```

#### Full script to parallelize Boto3-based code in AWS Glue


[AWS Glue Script - aws_glue_parallelize_full.py](aws_glue_parallelize_full.py)