import requests
from marshmallow import Schema, fields, post_load
from app.interfaces.hub_gateway import HubGateway

class ProcessedAgentDataSchema(Schema):
    road_state = fields.Str()
    agent_data = fields.Nested("AgentDataSchema")

    @post_load
    def make_processed_agent_data(self, data, **kwargs):
        return ProcessedAgentData(**data)


class HubHttpAdapter(HubGateway):
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.schema = ProcessedAgentDataSchema()

    def save_data(self, processed_data: ProcessedAgentData) -> bool:
        """
        Method to send the processed agent data to the specified HTTP endpoint.
        Parameters:
        processed_data: The processed agent data to be sent.
        Returns:
        bool: True if the data is successfully sent, False otherwise.
        """
        try:
            serialized_data = self.schema.dump(processed_data, many=True)
            response = requests.post(self.endpoint, json=serialized_data)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error sending processed data: {e}")
            return False