# 6. Read Consistency, Operations, and Transactions

## Reviewing read APIs

### PartiQL read operations

#### PartiQL `SELECT` examples with behavior similar to non-PartiQL DynamoDB APIs

```sql
-- table schema 
-- table name: Orders 
-- partition key: PK | sort key: SK 

-- similar to GetItem 
SELECT * 
FROM "Orders" 
WHERE PK = 'o#12345' AND SK = '!' 

-- similar to Query 
SELECT * 
FROM "Orders" 
WHERE PK = 'o#12345' 

-- similar to BatchGetItem 
SELECT * 
FROM "Orders" 
WHERE ((PK = 'o#12345' AND SK = 'p#1') 
        OR (PK = 'o#999' AND SK = 'p#5') 
        OR (PK = 'o#5567' AND SK = 'p#9')) 

-- similar to Scan 
SELECT * 
FROM "Orders" 
WHERE contains(non_key_attribute, '100') 
```

#### `ExecuteStatement` `SELECT` statement emulating batch/parallel `Query`
```sql
-- table schema 
-- table name: Orders 
-- partition key: PK | sort key: SK 

-- parallel Query-like 
SELECT * 
FROM "Orders"  
WHERE (
    (PK = 'o#12345')  
    OR (PK = 'o#999' 
        AND SK BETWEEN 's#2020-08-11T12:00:00Z' AND 's#2021-08-30T12:00:00Z')  
    OR (PK = 'o#5567' AND begins_with(SK, 'p#9'))
)
```

#### `TransactWriteItems` payload for bank transfer example
```json
{
     "TransactItems": [
        {
            "Put": {
                "TableName": "bank_accounts",
                "Item": {
                    "pk": {"S":"user#A"}, 
                    "sk": {"S":"line_item#txnId_123"}, 
                    "receiver": {"S":"user#B"},"value": {"N": "100"}
                }
            }
        },
        {
            "Put": {
                "TableName": "bank_accounts",
                "Item": {
                    "pk": {"S":"user#B"}, 
                    "sk": {"S":"line_item#txnId_123"}, 
                    "sender": {"S":"user#A"}, "value": {"N": "100"}
                }
            }
        },
        {
            "Update": {
                "TableName": "bank_accounts",
                "Key": {
                    "pk": {"S":"user#A"}, 
                    "sk": {"S":"account_balance"}
                },
                "UpdateExpression": "SET balance = balance - :1a200",
                "ConditionExpression": "balance > :1a200",
                "ExpressionAttributeValues": {":1a200": {"N":"100"}}
            }
        },
        {
            "Update": {
                "TableName": "bank_accounts",
                "Key": {
                    "pk": {"S":"user#B"}, 
                    "sk": {"S":"account_balance"}
                },
                "UpdateExpression": "SET balance = balance + :1a201",
                "ExpressionAttributeValues": {":1a201": {"N":"100"}}
            }
        }
    ]
} 
```