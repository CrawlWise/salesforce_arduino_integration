from simple_salesforce import Salesforce, SalesforceLogin, SFType
import json
import requests
import pandas

login = json.load(open("lCredentials.json")) #load my json credentials files
instance_url = login['instance_url']
payload = {
    'grant_type': 'password', # salesforce grant type
    'client_id': login['consumer_key'], # consumer key
    'client_secret': login['consumer_secret_key'], # consumer_secret_key
    'username': login['username'], # username
    'password': login['password'] # password
}

response = requests.post(instance_url + login['_endpoint'], data=payload)
print(response.json()) # This is to allow me retrieve my access token.
