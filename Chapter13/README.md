# 13. Global Tables

## Operating and managing global tables

### Converting a single-region table to a global table

#### `Query` using AWS CLI on London (eu-west-2) replica
```shell
aws dynamodb query \
    --table-name Employee \ 
    --key-condition-expression "LoginAlias = :pk_val" \
    --expression-attribute-values '{":pk_val": {"S": "amdhing"}}' \ 
    --region eu-west-2 | jq -rc
```

#### `Query` using AWS CLI on Singapore (ap-southeast-1) replica
```shell
aws dynamodb query \ 
    --table-name Employee \
    --key-condition-expression "LoginAlias = :pk_val" \ 
    --expression-attribute-values '{":pk_val": {"S": "amdhing"}}' \ 
    --region ap-southeast-1 | jq -rc
```