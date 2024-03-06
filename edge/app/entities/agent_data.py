from datetime import datetime
from pydantic import BaseModel, field_validator
from marshmallow import Schema, fields


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
        

class AccelerometerDataSchema(Schema):
    x = fields.Float()
    y = fields.Float()
    z = fields.Float()

class GpsDataSchema(Schema):
    latitude = fields.Float()
    longitude = fields.Float()

class AgentDataSchema(Schema):
    accelerometer = fields.Nested(AccelerometerDataSchema)
    gps = fields.Nested(GpsDataSchema)
    timestamp = fields.DateTime()