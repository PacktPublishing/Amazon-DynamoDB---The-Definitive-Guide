import json
import boto3
import random
import time
import uuid

sqs_client = boto3.client("sqs", region_name="eu-west-1")
TOTAL_SEGMENTS = 1000

# name of table to parallel scan and bulk process
TABLE_NAME="<mytable>" 

# SQS can parallelize processing using MessageGroups
# generating 200 groups for 1000 segments
# such that 200 Lambdas can process simultaneously
# and each group has 5 segments to process sequentially
group_shuff = [str(uuid.uuid4()) for x in range(0, 200)]

def lambda_handler(event, context):
    run_id = time.time()
    for segment in range(0, TOTAL_SEGMENTS):
        send_message({
            "TableName": TABLE_NAME,
            "TotalSegments": TOTAL_SEGMENTS,
            "Segment": segment,
            "RunId": run_id
        })
    return {
        'statusCode': 200,
        'body': json.dumps('All Tasks Submitted')
    }

def send_message(message):
    response = sqs_client.send_message(
        QueueUrl="https://sqs.eu-west-1.amazonaws.com/XXXX/table_scanner.fifo",
        MessageBody=json.dumps(message),
        MessageGroupId=random.choice(group_shuff)
    )
    print(response)