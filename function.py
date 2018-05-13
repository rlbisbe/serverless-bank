from repository.bank import Bank
from decimal import *
import json

def dispatch(event, context):
    requestContext = event["requestContext"]
    resourcePath = requestContext["resourcePath"]
    method = requestContext["httpMethod"]

    if(method == "GET"):
        payload = event['queryStringParameters']
    else:
        payload = json.loads(event['body']) # Load for file, loads for string

    try:

        if(resourcePath == "/account"):
            if(method == "PUT"):
                setup(payload)
                return {
                    "statusCode": 201
                }
                
            elif(method == "GET"):
                return {
                    "statusCode": 200,
                    "body": get_balance(payload)
                }

        elif(resourcePath == "/account/deposit"):
            deposit(payload)
            return {
                "statusCode": 200
            }

        elif(resourcePath == "/account/withdraw"):
            withdraw(payload)
            return {
                "statusCode": 200
            }

        elif(resourcePath == "/account/transfer"):
            transfer(payload)
            return {
                "statusCode": 200
            }

    except Exception:
        return {
            "statusCode": 500
        }

def setup(payload):
    account = payload['id']
    bank = Bank()
    bank.save_account({"id": account, "balance": 0})

def get_balance(payload):
    account = payload['id']
    bank = Bank()
    account = bank.get_account(account)

    if(account == None):
        raise Exception("invalid accoutn")
        
    return account['balance']

def deposit(payload):
    accountid = payload['id']
    amount = Decimal(payload['amount'])
    bank = Bank()
    account = bank.get_account(accountid)
    initial_balance = account['balance']
    account['balance'] = initial_balance + amount
    bank.log_transaction({"account_id": accountid, "transaction": "deposit", "amount": amount})
    bank.save_account(account)

def withdraw(payload):
    accountid = payload['id']
    amount = Decimal(payload['amount'])
    bank = Bank()
    account = bank.get_account(accountid)
    initial_balance = account['balance']
    if initial_balance < amount:
        raise Exception("invalid balance")

    account['balance'] = initial_balance - amount
    bank.log_transaction({"account_id": accountid, "transaction": "withdraw", "amount": -1 * amount})
    bank.save_account(account)
        

def transfer(payload):
    amount = Decimal(payload['amount'])
    bank = Bank()
    account_from = bank.get_account(payload['from'])
    account_to = bank.get_account(payload['to'])

    if(account_from != None and account_to != None and account_from['balance'] >= amount):
        account_from['balance'] -= amount
        account_to['balance'] += amount
        bank.log_transaction({"account_id": account_from['id'], "transaction": "send", "amount": -1 * amount})
        bank.log_transaction({"account_id": account_to['id'], "transaction": "receive", "amount": amount})
        bank.save_account(account_from)
        bank.save_account(account_to)
    else:
        raise Exception("invalid balance")
