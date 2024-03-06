from datetime import datetime
from pydantic import BaseModel, field_validator

class AccelerometerData(BaseModel):
    x: float
    y: float
    z: float

class GpsData(BaseModel):
    latitude: float
    longitude: float

class AgentData(BaseModel):
    accelerometer: AccelerometerData
    gps: GpsData
    timestamp: datetime
    @classmethod
    @field_validator('timestamp', mode='before')
    def parse_timestamp(cls, value):
        # Convert the timestamp to a datetime object
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            raise ValueError(
            "Invalid timestamp format. Expected ISO 8601 format(YYYY-MM-DDTHH:MM:SSZ).")
        
    def dict(self, *args, **kwargs):
        # Convert timestamp to ISO format string
        iso_timestamp = self.timestamp.isoformat()
        # Remove timestamp from the dictionary to avoid recursion error
        data_dict = super().dict(*args, **kwargs)
        data_dict['timestamp'] = iso_timestamp
        return data_dict