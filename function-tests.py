import unittest
import boto3
import function
import os
import json

# Before running this tests make sure you are running dynamodb local.
# https://aws.amazon.com/es/blogs/aws/dynamodb-local-for-desktop-development/
class TestFunction(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestFunction, self).__init__(*args, **kwargs)

        dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000') 
        dynamodb_client = boto3.client('dynamodb')

        try:
            table = dynamodb.create_table(
                TableName="Accounts",
                KeySchema=[
                    {
                        'AttributeName': 'id',
                        'KeyType': 'HASH'
                    }],
                    AttributeDefinitions=[
                    {
                        'AttributeName': 'id',
                        'AttributeType': 'S'
                    }],
                    ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                })
            table.meta.client.get_waiter('table_exists').wait(TableName='Accounts')
        except dynamodb_client.exceptions.ResourceInUseException:
            pass

        try:
            table = dynamodb.create_table(
                TableName="Transactions",
                KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                }],
                AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                }],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                })

            table.meta.client.get_waiter('table_exists').wait(TableName='Transactions')
        except dynamodb_client.exceptions.ResourceInUseException:
            pass

    def test_deposit(self):
        function.setup({'id': "Bob"})
        function.deposit({'id': "Bob", "amount": 10.0})
        self.assertEqual(function.get_balance({'id': "Bob"}), 10)

    def test_withdraw(self):   
        function.setup({'id': "Bob"})
        function.deposit({'id': "Bob", "amount": 10.0})
        function.withdraw({'id': "Bob", "amount": 10.0})
        self.assertEqual(function.get_balance({'id': "Bob"}), 0)

    def test_transfer(self):
        function.setup({'id': "Bob"})
        function.setup({'id': "Alice"})
        function.deposit({'id': "Bob", "amount": 10.0})
        function.deposit({'id': "Alice", "amount": 20.0})
        function.transfer({'from': "Alice", 'to': "Bob", 'amount': 5.0})
        self.assertEqual(function.get_balance({'id': "Bob"}), 15.0)
        self.assertEqual(function.get_balance({'id': "Alice"}), 15.0)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestFunction)
    unittest.TextTestRunner().run(suite)