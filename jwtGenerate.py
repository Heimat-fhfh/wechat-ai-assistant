#!/usr/bin/env python3
import sys
import time
import jwt
from define import WEATHER_PRIVATE_KEY,WEATHER_API_HOST,WEATHER_SUB_ID,WEATHER_KEY_ID

APIhost = WEATHER_API_HOST
# Open PEM
private_key = WEATHER_PRIVATE_KEY

def getJWT():
    payload = {
    'iat': int(time.time()) - 30,
    'exp': int(time.time()) + 900,
    'sub': WEATHER_SUB_ID
    }
    headers = {
        'kid': WEATHER_KEY_ID
    }
    return jwt.encode(payload, private_key, algorithm='EdDSA', headers = headers)

if __name__ == "__main__":
    # Generate JWT
    print(f"JWT:  {getJWT()}")
