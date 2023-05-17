#bimport the modules below by using navigating to the code folder and doing pip install <module name>
import json
import time

import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

# Class of Arduino  integration with salesforce
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
        Arduino_Salesforce = ArduinoToSalesforceIntegration()
        arduino_values = Arduino_Salesforce.generate_values_from_arduino_cloud()

        # Creating a post body header to send content to Salesforce cloud
        # The key names are the same as the fields names in Salesforce and the value are gotten
        # from line 78. Calling the method inside our class
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
        # Sending the post request to Salesforce cloud
        resp = requests.post(url=domain, headers=header, json=rdata)
        data = resp.json()
        return data

    #create the arduino update function
    def update_salesforce_object(self, sobject, record_id):

        # Generate my instan
        instance_url = self.login["salesforce_credentials"][0]['instance_url']
        domain = f"{instance_url}/services/data/v57.0/sobjects/Salesforce_Arduino_IoT_Integration__c/{record_id}"
        header = {
            "Authorization": f"Bearer {self.generate_salesforce_token()}",
            "Content-Type": "application/json"
        }

        arduino_Salesforce = ArduinoToSalesforceIntegration()
        arduino_values = arduino_Salesforce.generate_values_from_arduino_cloud()
        rdata = {
            "Battery_Percen__c": arduino_values[7]["last_value"],
            "Energy__c": arduino_values[0]["last_value"],
            "Input_Current__c": arduino_values[1]["last_value"],
            "Input_Power__c": arduino_values[2]["last_value"],
            "Input_Voltage__c": arduino_values[6]["last_value"],
            "Output_current__c": arduino_values[4]["last_value"],
            "Output_Power__c": arduino_values[5]["last_value"],
            "Output_Voltage__c": arduino_values[6]["last_value"],
            "Switch__c": arduino_values[8]["last_value"]
        }

        resp = requests.patch(url= domain, headers= header, data=json.dumps(rdata))
        data = resp.status_code
        if data == 204:
            print("data updated successfully")
        else:
            print("Data not updated.")

Arduino1_Salesforce = ArduinoToSalesforceIntegration()
#print(Arduino_Salesforce.salesforce_create_records())
#print(Arduino_Salesforce.generate_salesforce_token())
#print(Arduino1_Salesforce.update_salesforce_object("Salesforce_Arduino_IoT_Integration__c", "a018d00000N53b2"))


# Calling my instance class of create record
create_record = ArduinoToSalesforceIntegration()

# the while loop will keep running but only create a new data on salesforce when the switce value is set to true
# This is because when the switch value is off, no data on the arduino cloud will be updated.
while True:
    watcher = ArduinoToSalesforceIntegration()
    watcher_signal = watcher.generate_values_from_arduino_cloud()[8]['last_value']
    print("print im looping")
    if watcher_signal == True: # keep running and create object every 1 min once the data is set to true
        print("Salesforce will be updated every 5 minutes")
        create_record.salesforce_create_records()

        #starting my timer now
        time.sleep(60)
        if watcher_signal == False: # Return back to the while function body when data is set to fals
            print("Returning back to main loop")
            break


