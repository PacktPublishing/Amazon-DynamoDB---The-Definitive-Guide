# read from S3 export
df = glueContext.create_dynamic_frame.from_options(
    connection_type="s3", 
    connection_options={
        "compressionType": "gzip",
        "paths": ['s3://path/to/exported/data/']
        
    },
    format="json",
    transformation_ctx="df"
    ).toDF()

# issue UpdateItem API calls for each item
def process_item_update(boto3_table, item):
    # issue update_item calls here
    #
    # update_response = table.update_item(
    #       Key={'pk': 'foo', 'sk': 'bar'},
    #       ConditionExpression=Attr(NewAttribute).not_exists(),
    #       UpdateExpression='SET NewAttribute = :new_attr_val;,
    #       ExpressionAttributeValues={'NewAttribute': 'NewAttributeValue'},
    #       ReturnConsumedCapacity='INDEXES'
    #       )
    # handle throttles and condition check failure exceptions
    #
    #
    # return update_response
    
def execution_for_each_spark_partition(partitionData):
    # initialize boto3 clients on each Glue executor
    ddbclient = boto3.resource('dynamodb', region_name='eu-west-1', config=config)
    table = ddbclient.Table(TABLE_NAME)
     
    for item in partitionData:
        response = process_item_update(boto3_table, item)
    # use response and output of ReturnConsumedCapacity to rate-limit here
    
# convert to Spark RDD and parallelize
df1.rdd.foreachPartition(execution_for_each_spark_partition)