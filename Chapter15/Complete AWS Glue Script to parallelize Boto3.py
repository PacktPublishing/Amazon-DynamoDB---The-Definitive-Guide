import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

# write imports
import boto3 
from botocore.config import Config
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr, Key
import time

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

TASKS_PER_EXECUTOR = int(spark.sparkContext.getConf().get("spark.executor.cores"))
NUM_EXECUTORS = int(spark.sparkContext.getConf().get("spark.executor.instances"))
print("#### Tasks per executor: %d | Num executors: %d" % (TASKS_PER_EXECUTOR, NUM_EXECUTORS))

# init
TABLE_NAME = "mytable"
READ_THROUGHPUT_PERCENT = "1.0"
WRITE_THROUGHPUT_PERCENT = "1.0"
SPLITS_STR = str(NUM_EXECUTORS * TASKS_PER_EXECUTOR)
PK_ATTR_NAME = "PK"
SK_ATTR_NAME = "SK"

# Name of new GSISK attribute, eg: status#Timestamp
GSISK_ATTR_NAME = "GSISK"
# GSISK_ATTR_1 is attribute name of first part of GSISK value, eg: Status
GSISK_ATTR_1 = "Status"
# GSISK_ATTR_2 is attribute name of second part of GSISK value, eg: Timestamp
GSISK_ATTR_2 = "Timestamp"
config = Config(
   retries = {
      'max_attempts': 50,
      'mode': 'standard'
   },
   max_pool_connections = 1000
)

# driver boto3 client
ddbclient = boto3.resource('dynamodb', region_name='eu-west-1')
table = ddbclient.Table(TABLE_NAME)

# read
# 's3://mybucket/dynamodb/exports/timestamp_based_dummy_data/20210308/AWSDynamoDB/09898281524376-989ef139/data/'
# (optional) use boto3 before this step to manipulate ReadCapacityUnits on the table, wait until table in ACTIVE status
df = glueContext.create_dynamic_frame.from_options(
    connection_type="s3", 
    connection_options={
        "compressionType": "gzip",
        "paths": ['s3://mybucket/path/to/my/export/data/']
        
    },
    format="json",
    transformation_ctx="df"
    ).toDF()


# write
# (optional) use boto3 before this step to manipulate WriteCapacityUnits on the table, wait until table in ACTIVE status
if table.billing_mode_summary is not None and table.billing_mode_summary['BillingMode'] == 'PAY_PER_REQUEST':
    TOTAL_WCU_TARGET = float(WRITE_THROUGHPUT_PERCENT) * 40000
else:
    TOTAL_WCU_TARGET = float(WRITE_THROUGHPUT_PERCENT) * table.provisioned_throughput['WriteCapacityUnits']

MAX_WCU_PER_TASK = float(TOTAL_WCU_TARGET)/(TASKS_PER_EXECUTOR * NUM_EXECUTORS)

print("#### Max WCU per task: %f | Tasks per executor: %d | Num executors: %d | Splits: %s" % (MAX_WCU_PER_TASK, TASKS_PER_EXECUTOR, NUM_EXECUTORS, SPLITS_STR))


def get_time():
    return int(time.time())


# this function will be called for each item
def process_item_update(table, pk, sk, gsisk_attr1, gsisk_attr2):
    global PK_ATTR_NAME, SK_ATTR_NAME, GSIPK_ATTR_NAME, GSISK_ATTR_NAME, GSISK_ATTR_1, GSISK_ATTR_2
    update_response = None
    try:
        # issue update_item calls here
        # if gsisk_attr1 is not None and gsisk_attr2 is not None: # do nothing if GSISK attributes not present in data
        #     gsisk = str(gsisk_attr1['S']) + '#' + str(gsisk_attr2['S']) # combining value of resourceDomainId and lastModifiedTime
        # else:
        #     return update_response
        # update_response = table.update_item(
        #     Key={PK_ATTR_NAME:pk['S'], SK_ATTR_NAME: sk['S']},
        #     UpdateExpression="SET " + GSISK_ATTR_NAME + "=:gsisk", # GSISK_ATTR_NAME could be StatusTimestamp or GSISK, set in init block
        #     ConditionExpression= Attr(GSISK_ATTR_NAME).not_exists(), # ConditionCheck to only make update if StatusTimestamp/GSISK does not exist in live table data
        #     ExpressionAttributeValues={':gsisk': gsisk},
        #     ReturnConsumedCapacity='INDEXES'
        #     )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            # GSISK already exists in live table item, do nothing
            pass
        elif e.response['Error']['Code'] == 'ProvisionedThroughputExceededException':
            # Request throttled, retries exceeded, will try again
            update_response = process_item_update(table, pk, sk, gsisk_attr1, gsisk_attr2)
      
    return update_response


# foreachPartition function with token bucket algorithm based rate limiting
# This gets executed on each Glue DPU/worker in parallel. 
# On each worker, this will be further parallelized across TASKS_PER_EXECUTOR (default=4) threads
def execution_for_each_spark_partition(partitionData):
    global PK_ATTR_NAME, SK_ATTR_NAME, TABLE_NAME, GSIPK_ATTR_NAME, GSISK_ATTR_NAME, MAX_WCU_PER_TASK, GSISK_ATTR_1, GSISK_ATTR_2
    
    ddbclient = boto3.resource('dynamodb', region_name='eu-west-1', config=config)
    table = ddbclient.Table(TABLE_NAME)
    
    rate = MAX_WCU_PER_TASK # unit: WCU
    per  = 1 # unit: seconds
    allowance = rate # unit: WCU
    last_check = get_time() # unit: seconds

    task_item_count = 0 # counter to log progress

    for item in partitionData:
        current = get_time()
        time_passed = current - last_check;
        last_check = current
        allowance += time_passed * (rate / per)
        if allowance > rate:
            allowance = rate
        
        if allowance < 1.0: # no tokens remaining
            delta_time = float(get_time() + 1) - time.time()
            if delta_time > 0.0: 
                time.sleep(delta_time)
        
        response = process_item_update(table, item[PK_ATTR_NAME], item[SK_ATTR_NAME], item[GSISK_ATTR_1], item[GSISK_ATTR_2])
        task_item_count += 1
        # Using consumed capacity per request to rate limit
        if response is not None:
            total_consumed_capacity = response['ConsumedCapacity']
            tokens_to_deduct = total_consumed_capacity['Table']['CapacityUnits']
            # since LSI WCU is also consumed from table, we deduct additional tokens for rate limiting
            if 'LocalSecondaryIndexes' in total_consumed_capacity: 
                
                lsi_key_name = list(total_consumed_capacity['LocalSecondaryIndexes'].keys()) 
                lsi_name = lsi_key_name[0]
                tokens_to_deduct += total_consumed_capacity['LocalSecondaryIndexes'][lsi_name]['CapacityUnits']
            allowance -= tokens_to_deduct
            tokens_to_deduct = 0
        else:
            # response is None, due to ConditionCheckFailedException
            allowance -= 1
    print("#### Items processed for current task: %d" % task_item_count)
        
        
# First filter out only table PK/SK and attributes to combine for GSISK, then execute execution_for_each_spark_partition() function on each Glue worker in parallel            
df=df.select(PK_ATTR_NAME, SK_ATTR_NAME, GSISK_ATTR_1, GSISK_ATTR_2).rdd.foreachPartition(execution_for_each_spark_partition)

job.commit()
