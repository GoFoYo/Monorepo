import json
import logging
from typing import List
# import pydantic_core
import requests
from app.entities.processed_agent_data import ProcessedAgentData
from app.interfaces.store_api_gateway import StoreGateway
from config import BATCH_SIZE

class StoreApiAdapter(StoreGateway):
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url
    def save_data(self, processed_agent_data_batch: List[ProcessedAgentData]):
        if(len(processed_agent_data_batch) < BATCH_SIZE):
            return
        api_url = f"{self.api_base_url}/processed_agent_data"
        try:
            data_to_send = [item.dict() for item in processed_agent_data_batch]
            print("ACTION: HUB SEND DATA TO STORE")
            response = requests.post(api_url, json=data_to_send)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error sending processed data: {e}")
            return False