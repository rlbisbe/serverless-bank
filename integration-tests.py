import requests
import unittest
import boto3
import function
import os
import json

# Make sure you execute sam local start-api before running these tests 
class IntegrationTestFunction(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(IntegrationTestFunction, self).__init__(*args, **kwargs)

        requests.put('http://localhost:3000/account', data = json.dumps({'id':'test_bob'}))
        requests.put('http://localhost:3000/account', data = json.dumps({'id':'test_alice'}))

    def test_get_error(self):
        r = requests.get('http://localhost:3000/account?id=unknown_user')
        self.assertEqual(400, r.status_code)

    def test_deposit(self):
        r = requests.get('http://localhost:3000/account?id=test_bob')
        initial_bob_balance = float(r.text)

        r = requests.post('http://localhost:3000/account/deposit', data =  json.dumps({'id':'test_bob', 'amount': 100}))
        self.assertEqual(200, r.status_code)

        r = requests.get('http://localhost:3000/account?id=test_bob')
        new_balance = float(r.text)

        self.assertEqual(new_balance, initial_bob_balance + 100)

    def test_withdraw(self):
        r = requests.post('http://localhost:3000/account/deposit', data =  json.dumps({'id':'test_bob', 'amount': 100}))

        r = requests.get('http://localhost:3000/account?id=test_bob')
        initial_bob_balance = float(r.text)

        r = requests.post('http://localhost:3000/account/withdraw', data =  json.dumps({'id':'test_bob', 'amount': 5}))
        self.assertEqual(200, r.status_code)

        r = requests.get('http://localhost:3000/account?id=test_bob')
        new_balance = float(r.text)

        self.assertEqual(new_balance, initial_bob_balance - 5)

    def test_transfer(self):
        requests.post('http://localhost:3000/account/deposit', data =  json.dumps({'id':'test_bob', 'amount': 100}))
        requests.post('http://localhost:3000/account/deposit', data =  json.dumps({'id':'test_alice', 'amount': 70}))

        r = requests.get('http://localhost:3000/account?id=test_bob')
        initial_bob_balance = float(r.text)

        r = requests.get('http://localhost:3000/account?id=test_alice')
        initial_alice_balance = float(r.text)

        r = requests.post('http://localhost:3000/account/transfer', data =  json.dumps({'from':'test_bob', 'to': 'test_alice', 'amount': 20}))

        r = requests.get('http://localhost:3000/account?id=test_bob')
        bob_balance = float(r.text)

        r = requests.get('http://localhost:3000/account?id=test_alice')
        alice_balance = float(r.text)

        self.assertEqual(bob_balance, initial_bob_balance - 20)
        self.assertEqual(alice_balance, initial_alice_balance + 20)

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(IntegrationTestFunction)
    unittest.TextTestRunner().run(suite)