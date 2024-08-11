# 12. Streams and TTL

## DynamoDB Streams

### Consuming records from a DynamoDB Stream

#### Reading from DynamoDB Streams using AWSCLI

##### `CreateTable` input JSON
```json
{
    "AttributeDefinitions": [{
        "AttributeName": "PK",
        "AttributeType": "S"
    }],
    "TableName": "ddb_stream_table",
    "KeySchema": [{
        "AttributeName": "PK",
        "KeyType": "HASH"
    }],
    "BillingMode": "PROVISIONED",
    "ProvisionedThroughput": {
        "ReadCapacityUnits": 5,
        "WriteCapacityUnits": 5
    },
    "StreamSpecification": {
        "StreamEnabled": true,
        "StreamViewType": "NEW_AND_OLD_IMAGES"
    },
    "TableClass": "STANDARD"
}
```

##### `CreateTable` using AWS CLI
```shell
aws dynamodb create-table --cli-input-json file://create_table_input.json --region eu-west-2
```

##### `PutItem` using AWS CLI
```shell
TABLE=ddb_stream_table;

for PK_VALUE in {1..5}; do
    aws dynamodb put-item --table-name $TABLE \
        --item '{
            "PK": {"S": "'$PK_VALUE'"}, 
            "ATTR_1": {"S": "This is a static attribute"}
        }' \
        --region eu-west-2 ;
done
```

##### `DescribeStream` using AWS CLI
```shell
STREAM_ARN="arn:aws:dynamodb:eu-west-2:XXXX:table/ddb_stream_table/stream/2022-09-05T16:18:45.960"

aws dynamodbstreams describe-stream \
    --stream-arn "$STREAM_ARN" \
    --region eu-west-2
```

##### `GetShardIterator` using AWS CLI
```shell
STREAM_ARN="arn:aws:dynamodb:eu-west-2:XXXX:table/ddb_stream_table/stream/2022-09-05T16:18:45.960"
SHARD_ID="shardId-00000001662394728997-aabb"

aws dynamodbstreams get-shard-iterator \
    --stream-arn "$STREAM_ARN" \
    --shard-id "$SHARD_ID" \
    --shard-iterator-type TRIM_HORIZON \
    --region eu-west-2
```

##### `GetRecords` using AWS CLI
```shell
SHARD_ITERATOR="arn:aws:dynamodb:eu-west-2:XXXX:table/ddb_stream_table/stream/2022-09-05T16:18:45.960|1|AAAAAAAAAASomeRandomString=="

aws dynamodbstreams get-records \
    --shard-iterator "$SHARD_ITERATOR" \
    --region eu-west-2
```