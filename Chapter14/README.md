# 14. DynamoDB Accelerator (DAX) and Caching with DynamoDB

## Basics and setting up DAX

### Querying a DAX cluster

#### Python sample for Querying via DAX cluster
```python
from amazondax import AmazonDaxClient

# Initialize the Amazon DAX client with the endpoint URL and region
dax_client = AmazonDaxClient(
    endpoint_url='daxs://xxxx.yyyy.dax-clusters.eu-west-2.amazonaws.com',
    region_name='eu-west-2'
)

# Perform a query operation on the 'Employee' table
response = dax_client.query(
    TableName='Employee',
    KeyConditionExpression='LoginAlias = :pk_val',
    ExpressionAttributeValues={
        ':pk_val': {'S': 'ripani'}
    }
)

# Print the response from the query
print(response)
```

## Using DAX for high-volume delivery

#### Setting up logging and clients for DynamoDB and DAX
```python
import sys
import time
import logging
import boto3
import threading
import random
from amazondax import AmazonDaxClient
from botocore.config import Config

# Configuration constants
NUM_WRITES = 100000
NUM_READS = 200000
READ_CYCLE_MINUTES = 10
NUM_THREADS = 2

# Set up logger
logger = logging.getLogger()
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger.setLevel(logging.INFO)

TS_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

# Custom client configuration
my_config = Config(
    region_name='eu-west-2',
    max_pool_connections=100,
    retries={
        'max_attempts': 10,
        'mode': 'adaptive'
    }
)

# Set up the DynamoDB clients

# DynamoDB.Table resource for making batch writes
dynamodb = boto3.resource('dynamodb', region_name='eu-west-2', config=my_config)
table = dynamodb.Table('chapter14')

# DynamoDB.Client for making reads from DynamoDB
ddb_client = boto3.client('dynamodb', region_name='eu-west-2', config=my_config)

# Set up the DAX client
logger.info("Setting up DAX Client")
dynamodb_dax = AmazonDaxClient(
    endpoint_url='daxs://xxxx.yyyy.dax-clusters.eu-west-2.amazonaws.com',
    region_name='eu-west-2',
    config=my_config
)
```

#### Code snippet for dummy data generation
```python
# Generate dummy data
data = [
    {
        'PK': 'employee{}'.format(i),
        'Name': 'Employee {}'.format(i),
        'Age': random.randint(20, 50)
    } for i in range(NUM_WRITES)
]

# Insert the dummy data into the DynamoDB table
def put_items():
    with table.batch_writer() as batch:
        for item in data:
            batch.put_item(Item=item)

# Measure the time it takes to insert the dummy data
logger.info("Putting {} items into the DynamoDB table".format(NUM_WRITES))
start_time = time.time()
put_items()
end_time = time.time()

logger.info(
    "Time to insert data: {} seconds at {} Writes per second".format(
        end_time - start_time,
        NUM_WRITES / (end_time - start_time)
    )
)
```

#### Code snippet of `get_items` function
```python
# Define a function to perform GetItem requests

def get_items(client, thread_index, latencies, op_count_list):
    op_count = 0
    start_t = time.time()
    target_time = start_t + READ_CYCLE_MINUTES * 60

    while time.time() < target_time:
        for i in range(100):
            try:
                key = {'PK': {'S': 'employee{}'.format(random.randint(0, 9999))}}
                response = client.get_item(TableName='chapter14', Key=key)
                op_count += 1
            except Exception as e:
                print(e, file=sys.stderr)
        # time.sleep(0.01)

    end_t = time.time()
    total_t = end_t - start_t

    # adjusted_duration = (total_t - 0.01 * int(op_count / 100))
    adjusted_duration = total_t

    logger.info("Individual Thread Ended Execution. Number of Operations: {} at {} Reads per second"
                .format(op_count, (op_count / adjusted_duration)))

    latencies[thread_index] = adjusted_duration / op_count
    op_count_list[thread_index] = op_count
```

#### Code snippet of `measure_latency` function
```python
# Define a function to measure the time it takes to perform GetItem requests

def measure_latency(client, name):
    latencies = [None] * NUM_THREADS
    op_count_list = [None] * NUM_THREADS

    start_time = time.time()
    threads = [threading.Thread(target=get_items, args=(client, i, latencies, op_count_list)) 
               for i in range(NUM_THREADS)]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    end_time = time.time()
    duration = end_time - start_time

    logger.info("{} Latency Results: Total Time={} seconds, Average Latency={} ms"
                .format(name, duration, 1000 * (sum(latencies) / len(latencies))))
    
    return 1000 * (sum(latencies) / len(latencies))
```

#### Code snippet for calculating latency
```python
# Measure the latency of GetItem requests on the DynamoDB table

logger.info("Performing GetItem on same {} items directly to DynamoDB for {} minutes"
            .format(NUM_WRITES, READ_CYCLE_MINUTES))

ddb_avg = measure_latency(ddb_client, "DynamoDB")


# Measure the latency of GetItem requests on the DAX cluster

logger.info("Performing GetItem on same {} items via DAX for {} minutes"
            .format(NUM_WRITES, READ_CYCLE_MINUTES))

dax_avg = measure_latency(dynamodb_dax, "DAX")

logger.info("Repeated reading from DAX is {}% better than from DynamoDB"
            .format(100 * (1 - (dax_avg / ddb_avg))))
```
