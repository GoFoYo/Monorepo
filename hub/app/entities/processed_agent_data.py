from pydantic import BaseModel
from app.entities.agent_data import AgentData

class ProcessedAgentData(BaseModel):
    road_state: str
    agent_data: AgentData
    def dict(self, *args, **kwargs):
        # Remove agent_data from the dictionary to avoid recursion error
        data_dict = super().dict(*args, **kwargs)
        data_dict['agent_data'] = self.agent_data.dict()
        return data_dict