import json
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import iot_api_client as iot
from iot_api_client.rest import ApiException
from iot_api_client.configuration import Configuration
import pandas

login = json.load(open("lCredentials.json"))  # load my json credentials files

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
    return response.json()  # This is to allow me retrieve my access token.


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

#Creating an instance of the iot-api-client

#Query the thing information from Arduino Cloud
def thing_prop():
    thing_id = "4f3c278f-079d-46b6-b88a-3455f5d428dd"
    property_id = "778dfb53-36b4-43cd-a13c-59ac56227be7"

    url = f"https://api2.arduino.cc/iot/v2/things/{thing_id}/properties"
    header = {
        "content-type": "application/json",
        "Authorization": f"Bearer {generate_arduino_token()}",
    }
    resp = requests.get(url=url, headers=header)
    data_set = json.loads(resp.text)

    #Return the list from this item
    item_counts = len(data_set)
    for items in range(item_counts):
        dict_vals = data_set[items]
        name = dict_vals["name"]
        id = dict_vals['id']
        time_created = dict_vals['created_at']
        last_value_read = dict_vals['last_value']
        update_strategy = dict_vals['update_strategy']
        updated_at = dict_vals['updated_at']
        thing_id = dict_vals['thing_id']
        thing_name = dict_vals['thing_name']

        print(f"Name: {name}", end="\n")
        print(f'id: {id}', end="\n")
        print(f'Time Created: {time_created}', end="\n")
        print(f'Last Value Read: {last_value_read}', end="\n")
        print(f'Update Method: {update_strategy}', end="\n")
        print(f'Time Updated: {updated_at}', end="\n")
        print(f'Thing Name: {thing_name}', end="\n")
        print(f'Thing ID: {thing_id}', end="\n\n")

thing_prop()
