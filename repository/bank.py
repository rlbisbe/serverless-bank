import boto3
import os
import uuid

class Bank:

    def __init__(self):
        endpoint = os.environ.get("ENDPOINT")
        if(endpoint is None):
            self.dynamodb = boto3.resource('dynamodb')
        else:
            self.dynamodb = boto3.resource('dynamodb', endpoint_url=endpoint)

        self.accounts = self.dynamodb.Table("Accounts")
        self.transactions = self.dynamodb.Table("Transactions")

    def get_account(self, account_name):
        try:
            result = self.accounts.get_item(Key={'id': account_name})
            return result['Item']
        except:
            return None

    def log_transaction(self, transaction):
        transaction["id"] = str(uuid.uuid1())
        self.transactions.put_item(Item=transaction)

    def save_account(self, account):
        self.accounts.put_item(Item=account)
        