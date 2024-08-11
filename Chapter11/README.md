# 11. Backup, Restore, and More

## Understanding backup fundamentals

### Securing backups (and restores)

#### IAM policy example to secure DynamoDB managed on-demand backup
```json
{
    "Version": "2012-10-17", 
    "Statement": [{ 
        "Effect": "Deny",
        "Action": [
            "dynamodb:DeleteBackup",
            "dynamodb:RestoreTableFromBackup"
            ],
        "Resource": "arn:aws:dynamodb:*:123456789012:table/*"
    }] 
}
```

Additional resources
- [AWS Docs: Using IAM with DynamoDB backup and restore](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/backuprestore_IAM.html)

