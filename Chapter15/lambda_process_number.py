import json
import boto3
from botocore.config import Config
import time


# Initialize the DynamoDB client with custom configurations
DDB_CLIENT = boto3.client(
    'dynamodb',
    region_name='eu-west-1',
    config=Config(
        max_pool_connections=150,
        retries={
            'max_attempts': 20,
            'mode': 'standard'
        }
    )
)


def lambda_handler(event, context):
    """
    The entry point for AWS Lambda. Processes the incoming event and triggers the
    parallel processing of DynamoDB segments.

    Parameters:
        event (dict): The event dictionary containing input parameters such as 
                      segment number and run ID.
        context (object): The context in which the function is invoked.

    Returns:
        str: A string message indicating the count of processed items.
    """
    segment_number = event["number"]
    run_id = event["runId"]
    
    # Name of the table to scan
    table_name = '<mytable>'
    
    # Total segments should be the same as the length of the list returned by GenerateShuffledNumbers
    total_segments = 100
    
    return (
        "Ending Invocation with count:" + str(
            parallel_process(
                run_id,
                table_name,
                segment_number,
                total_segments
            )
        )
    )


def parallel_process(run_id: str, table_name: str, segment_number: int, total_segments: int = 30) -> int:
    """
    Processes a specific segment of a DynamoDB table in parallel, counts the items,
    and updates a result table with the item count.

    Parameters:
        run_id (str): A unique identifier for the current run.
        table_name (str): The name of the DynamoDB table to scan.
        segment_number (int): The segment number to process in parallel.
        total_segments (int): The total number of segments the table is divided into. Default is 30.

    Returns:
        int: The total count of items processed in the specified segment.
    """
    count = 0
    kwargs = {
        'TableName': table_name,
        'TotalSegments': total_segments,
        'Segment': segment_number,
        'Select': 'COUNT'
    }
    
    while True:
        scan_response = DDB_CLIENT.scan(**kwargs)
        
        # Bulk processing logic would go here
        # for item in scan_response:
        #     do something
        
        count += scan_response.get('Count', 0)
        last_evaluated_key = scan_response.get('LastEvaluatedKey', None)
        kwargs.update({'ExclusiveStartKey': last_evaluated_key})
        
        if last_evaluated_key is None:
            # Log total number of items scanned
            # Can use transact_write_items() for idempotency
            DDB_CLIENT.update_item(
                # Name of the table to log item counts to
                TableName='<result table>',
                Key={
                    'uuid': {'S': table_name},
                    'sort_id': {'N': str(run_id)}
                },
                UpdateExpression="SET item_count = if_not_exists(item_count, :zero_var) + :new_var",
                ExpressionAttributeValues={
                    ':zero_var': {'N': '0'},
                    ':new_var': {'N': str(count)}
                }
            )
            return count
