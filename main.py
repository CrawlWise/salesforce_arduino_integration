import json
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import iot_api_client as iot
from iot_api_client.rest import ApiException
from iot_api_client.configuration import Configuration
import pandas as pd

login = json.load(open("auth.json"))  # load my json credentials files

def generate_salesforce_token():
    instance_url = login["salesforce_credentials"][0]['instance_url']
    payload = {
        'grant_type': 'password',  # salesforce grant type
        'client_id': login["salesforce_credentials"][0]['consumer_key'],  # consumer key
        'client_secret': login["salesforce_credentials"][0]['consumer_secret_key'],  # consumer_secret_key
        'username': login["salesforce_credentials"][0]['username'],  # username
        'password': login["salesforce_credentials"][0]['password']  # password
    }

    response = requests.post(instance_url + login["salesforce_credentials"][0]['_endpoint'], data=payload)
    data = response.json()  # This is to allow me retrieve my access token.
    return data['access_token']

def generate_arduino_token():
    client_id = "jJL7xknfC5knAni2qeOZgXJcWMUmgr0D"
    client_secret = "sl7y9mF2QW5vfsRWdQR3o4Z9rJ40GmisAVNNOGyaXRPWs1CVEljkHn7Clsp4xTF3"
    oauth_client = BackendApplicationClient(client_id=client_id)
    token_url = "https://api2.arduino.cc/iot/v1/clients/token"

    oauth = OAuth2Session(client=oauth_client)
    token = oauth.fetch_token(
        token_url=login["arduino_credentials"][0]["token_url"],
        client_id=login["arduino_credentials"][0]["client_id"],
        client_secret=login["arduino_credentials"][0]["client_secret"],
        include_client_id=True,
        audience="https://api2.arduino.cc/iot"
    )
    return token.get("access_token")

# Generate the all values from of the variables in arduino cloud
def generate_values_from_arduino_cloud():
    """
    the generate_values_from_arduino_cloud functions return all the keys and values of Arduino thing based on a specific thing id.
    :return: Thing object ID
    """
    thing_id = "4f3c278f-079d-46b6-b88a-3455f5d428dd"

    url = f"https://api2.arduino.cc/iot/v2/things/{thing_id}/properties"
    header = {
        "content-type": "application/json",
        "Authorization": f"Bearer {generate_arduino_token()}",
    }
    resp = requests.get(url=url, headers=header)
    data_set = json.loads(resp.text)
    #Return the list from this item
    item_counts = len(data_set)
    data_values = [data for data in data_set]
    return data_values

def salesforce_create_records(name, id, time_created, last_value_read, update_strategy, update_at, thing_id, thing_name):
    """
    This creates the records on Sobject based on the object name provided on the url. IN other to specify the object you
    want to modify, update the domain url {sobject} /services/data/v57.0/sobjects/{sobject}/" to the name of the update
    you want to create records.
    :param name: required
    :param id: required. This is a unique field in the Sobject bucket
    :param time_created:
    :param last_value_read:
    :param update_strategy:
    :param update_at:
    :param thing_id:
    :param thing_name:
    :return:
    """
    instance_url = login["salesforce_credentials"][0]['instance_url']
    domain = f"{instance_url}/services/data/v57.0/sobjects/Salesforce_Arduino_integration__c/"
    header = {
        "Authorization": f"Bearer {generate_salesforce_token()}",
        "Content-Type": "application/json"
    }

    rdata = {
        "name":name,
        "device_ID__c": id,
        "time_created__c": time_created,
        "last_value_read__c": last_value_read,
        "update_strategy__c": update_strategy,
        "time_updated__c": update_at,
        "thing_id__c": thing_id,
        "thing_name__c": thing_name
    }

    resp = requests.post(url=domain, headers=header, json=rdata)
    data = resp.json()
    print(data)


# Get all Salesforce_Arduino_integration object Id
def query_record_id():
    instance_url = instance_url = login["salesforce_credentials"][0]['instance_url']  # This hold my domain name url gotten from a json file
    query = "SELECT+id+FROM+Salesforce_Arduino_integration__c"
    domain = f"{instance_url}/services/data/v57.0/query/?q={query}"
    header = {
        "Authorization": f"Bearer {generate_salesforce_token()}",
        "Content-Type": "application/json"
    }

    resp = requests.get(url=domain, headers=header)
    data = json.loads(resp.text)
    data_records = data['records']
    #format_json = json.dumps(data_records, indent=2)
    #print(format_json)

    return data['records']



def update_saleforce_records(sobject):
    instance_url = login["salesforce_credentials"][0]['instance_url'] # This hold my domain name url gotten from a json file
    domain = f"{instance_url}/services/data/v57.0/sobjects/Salesforce_Arduino_integration__c/"
    header = {
        "Authorization": f"Bearer {generate_salesforce_token()}",
        "Content-Type": "application/json"
    }

    #Getting ID from salesforce Object
    for ID in query_record_id():
        data_id = (ID["Id"])

    # Get Data from Arduino Cloud and loop each data into the variable to be used by requests method

        for x in generate_values_from_arduino_cloud():
            name = x['name']
            id = data_id
            time_created = x['created_at']
            last_value = x['last_value']
            update_strategy = x['update_strategy']
            update_at = x['updated_at']
            thing_id = x['thing_id']
            thing_name = x['thing_name']

            rdata = {
                "name": name,
                "device_ID__c": id,
                "time_created__c": time_created,
                "last_value_read__c": last_value,
                "update_strategy__c": update_strategy,
                "time_updated__c": update_at,
                "thing_id__c": thing_id,
                "thing_name__c": thing_name
            }

        update_record = requests.post(url=domain, headers=header, json=rdata)
        resp_code = update_record.json()
        print(resp_code)

#update_saleforce_records("Salesforce_Arduino_integration__c")


for x in generate_values_from_arduino_cloud():
    name = x['name']
    id = x['id']
    time_created = x['created_at']
    last_value = x['last_value']
    update_strategy = x['update_strategy']
    update_at = x['updated_at']
    thing_id = x['thing_id']
    thing_name = x['thing_name']

    salesforce_create_records(name, id, time_created, last_value, update_strategy, update_at, thing_id, thing_name)
