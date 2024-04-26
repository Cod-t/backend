import urllib.request
import json
import os
import ssl

def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.

# Request data goes here
# The example below assumes JSON formatting which may be updated
# depending on the format your endpoint expects.
# More information can be found here:
# https://docs.microsoft.com/azure/machine-learning/how-to-deploy-advanced-entry-script
data =  {
  "Inputs": {
    "data": [
      {
        "Sex": "Female",
        "Year.of.diagnosis": 2008,
        "Race.recode..W..B..AI..API.": "Black",
        "treatment": "surg only",
        "Year.of.follow.up.recode": 2022,
        "Breast": True,
        "Endocrine": False,
        "Eye, and adnexa": False,
        "Gastrointestinal": True,
        "Gynecological": False,
        "Head and Neck": False,
        "hematopoietic": False,
        "Male Genital": False,
        "Musculoskeletal": False,
        "Nervous System": False,
        "Respiratory": False,
        "Skin": False,
        "Unspecified": False,
        "Urinary": False,
        "Age": 97
      }
    ]
  },
  "GlobalParameters": {
    # "method": "predict",
    "method": "predict_proba"
  }
}

body = str.encode(json.dumps(data))

url = 'http://5ab60f81-79a1-4dd1-be2b-500e0a07e324.eastus2.azurecontainer.io/score'
# Replace this with the primary/secondary key, AMLToken, or Microsoft Entra ID token for the endpoint
api_key = 'PQkDDTwcaGTRiHmmMlQRijc4Z1gbZERr'
if not api_key:
    raise Exception("A key should be provided to invoke the endpoint")


headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}

req = urllib.request.Request(url, body, headers)

try:
    response = urllib.request.urlopen(req)

    result = response.read()
    print(result)
except urllib.error.HTTPError as error:
    print("The request failed with status code: " + str(error.code))

    # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
    print(error.info())
    print(error.read().decode("utf8", 'ignore'))