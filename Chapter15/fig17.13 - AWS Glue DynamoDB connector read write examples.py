# reading from DynamoDB table using parallel Scan 

dyf = glue_context.create_dynamic_frame.from_options( 
    connection_type="dynamodb", 
    connection_options={"dynamodb.input.tableName": test_source, 
        "dynamodb.throughput.read.percent": "1.0" 
    } 
) 

# writing into DynamoDB table using BatchWriteItem 

glue_context.write_dynamic_frame_from_options( 
    frame=dyf, 
    connection_type="dynamodb", 
    connection_options={"dynamodb.output.tableName": test_sink, 
        "dynamodb.throughput.write.percent": "1.0" 
    } 
) 