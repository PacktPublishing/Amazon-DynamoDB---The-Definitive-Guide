import json
import boto3
from botocore.config import Config
import time


DDB_CLIENT = boto3.client(
    "dynamodb",
    region_name="eu-west-1",
    config=Config(
        max_pool_connections=150, retries={"max_attempts": 20, "mode": "standard"}
    ),
)


def lambda_handler(event, context):
    segment_number = event["number"]
    run_id = event["runId"]

    # name of table to scan
    table_name = "<mytable>"

    # total segments to be same as length of list returned by GenerateShuffledNumbers
    total_segments = 100

    return "Ending Invocation with count:" + str(
        parallel_process(run_id, table_name, segment_number, total_segments)
    )


def parallel_process(
    run_id: str, table_name: str, segment_number: int, total_segments: int = 30
) -> None:
    count = 0

    kwargs = {
        "TableName": table_name,
        "TotalSegments": total_segments,
        "Segment": segment_number,
        "Select": "COUNT",
    }

    while True:
        scan_response = DDB_CLIENT.scan(**kwargs)

        # bulk processing logic to go here
        # for item in scan_response:
        #     do something
        #

        count += scan_response.get("Count", 0)
        last_evaluated_key = scan_response.get("LastEvaluatedKey", None)
        kwargs.update({"ExclusiveStartKey": last_evaluated_key})

        if last_evaluated_key is None:
            # log total number of items scanned
            # can use transact_write_items() for idempotency

            DDB_CLIENT.update_item(
                # name of table to log item counts to
                TableName="<result table>",
                Key={"uuid": {"S": table_name}, "sort_id": {"N": str(run_id)}},
                UpdateExpression="SET item_count = if_not_exists(item_count, :zero_var) + :new_var",
                ExpressionAttributeValues={
                    ":zero_var": {"N": "0"},
                    ":new_var": {"N": str(count)},
                },
            )

            return count
