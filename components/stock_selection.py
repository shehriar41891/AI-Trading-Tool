from polygon import RESTClient
import json 
from typing import cast
from urllib3 import HTTPResponse
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os 

load_dotenv()

POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')

#connecting to polygon api 
client = RESTClient(
    POLYGON_API_KEY
)

aggs = cast(
    HTTPResponse,
    client.get_aggs(
        'AAPL',
        1, #per day
        'minute',
        '2024-09-20',
        '2025-01-15',
        raw = True
    )
)

data = json.loads