#bimport the modules below by using navigating to the code folder and doing pip install <module name>
import json
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session


class ArduinoToSalesforceIntegration:
    # Load my json file
    login = json.load(open("auth.json"))

    # Get my Salesforce instance url from json file auth.json
    instance_url = login["salesforce_credentials"][0]['instance_url']

    # Creating my method to generate token from salesforce
    def generate_salesforce_token(self):
        instance_url = self.login["salesforce_credentials"][0]['instance_url']
        payload = {
            'grant_type': 'password',  # salesforce grant type
            'client_id': self.login["salesforce_credentials"][0]['consumer_key'],  # consumer key
            'client_secret': self.login["salesforce_credentials"][0]['consumer_secret_key'],  # consumer_secret_key
            'username': self.login["salesforce_credentials"][0]['username'],  # username
            'password': self.login["salesforce_credentials"][0]['password']  # password
        }

        response = requests.post(instance_url + self.login["salesforce_credentials"][0]['_endpoint'], data=payload)
        data = response.json()  # This is to allow me retrieve my access token.
        return data['access_token']

    # Creating my method to generate token from Arduino IoT Cloud
    def generate_arduino_token(self):
        client_id = self.login["arduino_credentials"][0]["client_id"] # This generates my client ID from my Json file
        oauth_client = BackendApplicationClient(client_id=client_id) # Authenticating to arduino using my token generate from arduino cloud
        oauth = OAuth2Session(client=oauth_client)

        # Creating a token dictionary to retrieve access token from arduino cloud
        token = oauth.fetch_token(
            token_url=self.login["arduino_credentials"][0]["token_url"],
            client_id=client_id,
            client_secret=self.login["arduino_credentials"][0]["client_secret"],
            include_client_id=True,
            audience="https://api2.arduino.cc/iot"
        )
        return token.get("access_token")

    # Generating values from Arduino cloud to be created in Salesforce platform
    def generate_values_from_arduino_cloud(self):
        """
        the generate_values_from_arduino_cloud functions return all the keys and values of Arduino thing based on a specific thing id.
        :return: Thing object ID
        """
        thing_id = "4f3c278f-079d-46b6-b88a-3455f5d428dd" # Thing id gotten from the arduino IoT Cloud
        url = f"https://api2.arduino.cc/iot/v2/things/{thing_id}/properties"
        header = {
            "content-type": "application/json",
            "Authorization": f"Bearer {self.generate_arduino_token()}",
        }
        resp = requests.get(url=url, headers=header)
        data_set = json.loads(resp.text)
        # Return the list from this item
        item_counts = len(data_set)
        data_values = [data for data in data_set]
        return data_values


    # Create the record to Salesforce cloud
    def salesforce_create_records(self):

        instance_url = self.login["salesforce_credentials"][0]['instance_url']
        domain = f"{instance_url}/services/data/v57.0/sobjects/Salesforce_Arduino_IoT_Integration__c"
        header = {
            "Authorization": f"Bearer {self.generate_salesforce_token()}",
            "Content-Type": "application/json"
        }
        # Generating the values of Arduino thing into salesforce
        arduino_values = Arduino_Salesforce.generate_values_from_arduino_cloud()

        # Creating a post body header to send content to Salesforce cloud
        rdata = {
            "Battery_Percen__c": arduino_values[7]["last_value"],
            "Device_ID__c": "4f3c278f-079d-46b6-b88a-3455f5d428dd",
            "Energy__c": arduino_values[0]["last_value"],
            "Input_Current__c": arduino_values[1]["last_value"],
            "Input_Power__c": arduino_values[2]["last_value"],
            "Input_Voltage__c": arduino_values[6]["last_value"],
            "Output_current__c": arduino_values[4]["last_value"],
            "Output_Power__c": arduino_values[5]["last_value"],
            "Output_Voltage__c": arduino_values[6]["last_value"],
            "Switch__c": arduino_values[8]["last_value"]
        }

        resp = requests.post(url=domain, headers=header, json=rdata)
        data = resp.json()
        return data.stat


Arduino_Salesforce = ArduinoToSalesforceIntegration()
print(Arduino_Salesforce.salesforce_create_records())
#print(Arduino_Salesforce.generate_salesforce_token())
