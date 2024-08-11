import json
import boto3
import random
import time
import uuid

# Initialize the SQS client for the specified region
sqs_client = boto3.client("sqs", region_name="eu-west-1")

# Total number of segments for parallel processing
TOTAL_SEGMENTS = 1000

# Name of the DynamoDB table to parallel scan and bulk process
TABLE_NAME = "<mytable>"

# Generate 200 unique UUIDs for SQS Message Groups to parallelize processing
# These groups will handle 1000 segments, allowing 200 Lambdas to process simultaneously
# Each group will sequentially process 5 segments
group_shuff = [str(uuid.uuid4()) for _ in range(200)]


def lambda_handler(event, context):
    """
    AWS Lambda handler function that initiates the parallel scanning and processing
    of a DynamoDB table by sending messages to an SQS queue. Each message represents
    a segment to be processed.

    Parameters:
        event (dict): The event triggering the Lambda function. Not used in this implementation.
        context (object): The context in which the Lambda function is invoked. Not used in this implementation.

    Returns:
        dict: A dictionary containing:
              - 'statusCode': HTTP status code indicating success.
              - 'body': A message indicating that all tasks have been submitted.
    """
    # Generate a unique run ID based on the current time
    run_id = time.time()

    # Send a message to the SQS queue for each segment
    for segment in range(TOTAL_SEGMENTS):
        send_message({
            "TableName": TABLE_NAME,
            "TotalSegments": TOTAL_SEGMENTS,
            "Segment": segment,
            "RunId": run_id
        })

    # Return a success message
    return {
        'statusCode': 200,
        'body': json.dumps('All Tasks Submitted')
    }


def send_message(message):
    """
    Sends a message to an SQS queue with the given message body and a randomly
    selected MessageGroupId from the predefined group_shuff list.

    Parameters:
        message (dict): The message body to be sent to the SQS queue, containing
                        details about the DynamoDB segment to be processed.

    Returns:
        None: This function does not return a value. It prints the response from SQS.
    """
    response = sqs_client.send_message(
        QueueUrl="https://sqs.eu-west-1.amazonaws.com/XXXX/table_scanner.fifo",
        MessageBody=json.dumps(message),
        MessageGroupId=random.choice(group_shuff)
    )

    # Print the response from the SQS send_message operation
    print(response)
