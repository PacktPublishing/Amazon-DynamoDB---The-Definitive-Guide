# get job infrastructure details to parallelize processing efficiently
TASKS_PER_EXECUTOR = int(spark.sparkContext.getConf().get("spark.executor.cores"))
NUM_EXECUTORS = int(spark.sparkContext.getConf().get("spark.executor.instances"))
print("#### Tasks per executor: %d | Num executors: %d" % (TASKS_PER_EXECUTOR, NUM_EXECUTORS))

WRITE_THROUGHPUT_PERCENT = "1.0"
SPLITS_STR = str(NUM_EXECUTORS * TASKS_PER_EXECUTOR)

# use infrastructure details and WRITE_THROUGHPUT_PERCENT to compute max WCU per spark partition
# MAX_WCU_PER_TASK obtained will be used to rate-limit on individual spark partition/Glue worker level
if table.billing_mode_summary is not None and table.billing_mode_summary['BillingMode'] == 'PAY_PER_REQUEST':
    TOTAL_WCU_TARGET = float(WRITE_THROUGHPUT_PERCENT) * 40000
else:
    TOTAL_WCU_TARGET = float(WRITE_THROUGHPUT_PERCENT) * table.provisioned_throughput['WriteCapacityUnits']

MAX_WCU_PER_TASK = float(TOTAL_WCU_TARGET)/(TASKS_PER_EXECUTOR * NUM_EXECUTORS)

print("#### Max WCU per task: %f | Tasks per executor: %d | Num executors: %d | Splits: %s" % (MAX_WCU_PER_TASK, TASKS_PER_EXECUTOR, NUM_EXECUTORS, SPLITS_STR))


# issue UpdateItem API calls for each item
def process_item_update(boto3_table, item):
    update_response = None
    try:
        # bulk processing logic here
        # do something
        # 
    # handle ProvisionedThroughputExceededException and ConditionCheckFailedExceptions
    # if ConditionCheckFailedException, return None
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            # Condition failed, do nothing
            pass
        elif e.response['Error']['Code'] == 'ProvisionedThroughputExceededException':
            # Request throttled, retries exceeded, will try again
            update_response = process_item_update(boto3_table, item)
    
    return update_response
    
# This gets executed on each Glue worker in parallel. 
# On each worker, this will be further parallelized across TASKS_PER_EXECUTOR (default=4) threads
def execution_for_each_spark_partition(partitionData):
    global MAX_WCU_PER_TASK
    
    # initialize boto3 client
    # table = ddbclient.table(TABLE_NAME)
    
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
        
        response = process_item_update(table, item)
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