# HR_test

![Alt text](pipeline.png)


# How to access the API

In this tutorial, you'll learn how to use a Flask API that allows you to retrieve load details from a CSV file, given a reference_number. The API is protected by an API key for authentication, which you will need to include in your request.



## Step 1: Get Your API Key
Before you can start using the API, you need to obtain a valid API key. This key is used to authenticate your requests.

Contact the API provider to request an API key.

The key will be hashed and stored in the database, and you will use it in the Authorization header of your requests.


## Step 2: Making a Request to the API

## /load Endpoint

The endpoint we will interact with is `/loads`. This endpoint allows you to retrieve load details by providing a `reference_number`.

### Request Details:

- **URL**: `https://robothappy-d5e4eyaafhf5dyct.canadacentral-01.azurewebsites.net`
- **Method**: `GET`
- **Authorization Header**: You must include a Bearer token (API key) for authentication.
- **Request Body**: You must send a JSON object containing the `reference_number`.


#### Example using cURL
If you prefer using the command line, you can use cURL to make the API request. Here’s an example:

``` bash 

curl -X GET https://robothappy-d5e4eyaafhf5dyct.canadacentral-01.azurewebsites.net/loads \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"reference_number": "12345"}'

```

#### Understanding the Response
Once you make the request, the API will send a response.

#### Success Response:
If the reference_number is valid and the API key is authenticated, you'll get a JSON response with the load details:

- reference_number: Unique identifier for each load.
- origin: The starting location of the load.
- destination: The final destination of the load.
- equipment_type: The type of equipment required (e.g., Dry Van,
Flatbed). 
- rate: The rate associated with the load.
- commodity: The type of goods being transported.

``` json
{   
    "reference_number": "REF09690",
    "origin": "Detroit, MI",
    "destination": "Nashville, TN",
    "equipment_type": "Dry Van",
    "rate": "1495",
    "commodity": "Industrial Equipment"
    
}
```


#### Error Responses:
Unauthorized Error: If your API key is invalid or missing, you will get a 401 Unauthorized error:

``` json
{
  "error": "Unauthorized"
}
```
Bad Request: If you don’t include the reference_number or if it’s invalid, you will get a 400 Bad Request error:



``` json
{
  "error": "Reference number is required"
}
```

Not Found: If the load with the specified reference_number does not exist, you will receive a 404 Not Found error:


``` json
{
  "error": "Load not found."
}
```


## /verify_carrier Endpoint


The /verify_carrier endpoint allows you to verify a carrier by providing an MC (Motor Carrier) number.

### Request Details:

- **URL**: `https://robothappy-d5e4eyaafhf5dyct.canadacentral-01.azurewebsites.net`
- **Method**: `POST`
- **Authorization Header**: You must include a Bearer token (API key) for authentication.
- **Request Body**: You must send a JSON object containing the `mc_number`.



#### Example using cURL
Here’s an example of how to use cURL to make the API request:

``` bash 

curl -X POST https://your-api-endpoint.com/verify_carrier \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"mc_number": "123456"}'
```

#### Understanding the Response
Once you make the request, the API will send a response indicating whether the carrier is valid and allowed to operate. The API will provide additional next steps for further verification or action based on the response.

#### Success Response:
If the MC number is valid and the carrier exists, the response will indicate whether the carrier is allowed to operate.

- **allowed_to_operate**: Whether the carrier is authorized to operate.

- **legal_name**: The legal name of the carrier.

- **next_steps**: A set of instructions based on whether the carrier is verified and allowed to operate.



``` json
{
  "carrier": {
    "legal_name": "Example Carrier Inc.",
    "allowed_to_operate": true
  },
  "next_steps": {
    "1": "Confirm you found the right carrier name. Ask user exactly this: 'Example Carrier Inc.?'. Then wait for user to respond.",
    "2": {
      "a": "If user confirms: move on to finding available loads, MAKE SURE you do not give them load information until you have verified they work for 'Example Carrier Inc.'",
      "b": "If user denies: first, you must ask the user to repeat the name of the carrier they work for ('I'm sorry, I didn't quite catch that. What's the name of the carrier you work for?'). Wait for the user to provide the name again and check if it matches the carrier name you have.",
      "c": "If you still cannot verify the carrier name, ask the user for their MC number ('I'm sorry, what's that MC number again?'). Wait for user to provide number again. Then search for the carrier again with new number the caller provides."
    }
  }
}
```

#### Example of a Carrier Not Allowed to Operate:

``` json
{
  "carrier": {
    "allowed_to_operate": false
  },
  "message": "Carrier is not allowed to operate.",
  "next_steps": {
    "1": "Inform the user that this carrier is not allowed to operate.",
    "2": {
      "a": "Politely let the user know that they will need to verify with FMCSA why their carrier is restricted.",
      "b": "If the user insists, offer to check another carrier by asking for a different MC number.",
      "c": "If the user cannot provide another MC number, suggest they contact FMCSA directly for more details."
    }
  }
}
```

#### Error Responses:
If the request is invalid or missing required information, the following error responses may occur.

**Unauthorized Error**: If your API key is invalid or missing, you will get a 401 Unauthorized error:

``` json
{
  "error": "Unauthorized"
}
```


**Bad Request**: If the mc_number is not included or is invalid, you will get a 400 Bad Request error:


``` json
{
  "error": "MC number is required"
}
```

**Carrier Not Found**: If the carrier with the given MC number is not found in the FMCSA database:

``` json
{
  "error": "Carrier not found.",
  "next_steps": {
    "1": "Inform the user that no carrier was found under the given MC number.",
    "2": {
      "a": "Ask the user to repeat the MC number to ensure it was entered correctly.",
      "b": "If the user provides a new number, attempt to search for the carrier again.",
      "c": "If no carrier is still found, suggest the user verify their carrier information with FMCSA."
    }
  }
}
```