from config import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
from sqlalchemy import create_engine, MetaData, text, Table, Column, Integer, String, Float, DateTime
from sqlalchemy.dialects.postgresql import insert
from pydantic import BaseModel, ValidationError, ValidationInfo, ValidatorFunctionWrapHandler, validator
from datetime import datetime
from fastapi import FastAPI, WebSocket, HTTPException
from typing import Set, List
import asyncio
import json

# SQLAlchemy setup
DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define the ProcessedAgentData table
processed_agent_data = Table(
"processed_agent_data",
metadata,
Column("id", Integer, primary_key=True, index=True),
Column("road_state", String),
Column("x", Float),
Column("y", Float),
Column("z", Float),
Column("latitude", Float),
Column("longitude", Float),
Column("timestamp", DateTime),
)

def test_connection():
    try:
        with engine.connect() as conn:
            # Create a SQL expression using SQLAlchemy's text() function
            query = text('SELECT 1')
            # Execute the query
            result = conn.execute(query)
            # Fetch the result (optional)
            row = result.fetchone()
            # Print the result
            print("Database connection successful:", row[0] == 1)
    except Exception as e:
        print("Error connecting to the database:", e)

# FastAPI models
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
    @validator('timestamp')
    def check_timestamp(cls, value):
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            raise ValueError("Invalid timestamp format. Expected ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).")
    def dict(self, *args, **kwargs):
        # Convert timestamp to ISO format string
        iso_timestamp = self.timestamp.isoformat()
        # Remove timestamp from the dictionary to avoid recursion error
        data_dict = super().dict(*args, **kwargs)
        data_dict['timestamp'] = iso_timestamp
        return data_dict

class ProcessedAgentData(BaseModel):
    road_state: str
    agent_data: AgentData
    def dict(self, *args, **kwargs):
        # Remove agent_data from the dictionary to avoid recursion error
        data_dict = super().dict(*args, **kwargs)
        data_dict['agent_data'] = self.agent_data.dict()
        return data_dict

# Database model
class ProcessedAgentDataInDB(BaseModel):
    id: int
    road_state: str
    x: float
    y: float
    z: float
    latitude: float
    longitude: float
    timestamp: datetime


# FastAPI app setup
app = FastAPI()
# WebSocket subscriptions
subscriptions: Set[WebSocket] = set()
# FastAPI WebSocket endpoint
@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    subscriptions.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        subscriptions.remove(websocket)

# Function to send data to subscribed users
async def send_data_to_subscribers(data):
    for websocket in subscriptions:
        data1 = [agent_data.dict() for agent_data in data]
        # message = json.dumps(data1)
        print('Send data WS', data1)
        await websocket.send_json(data1)


@app.post("/processed_agent_data/")
async def create_processed_agent_data(data: List[ProcessedAgentData]):
    print("ACTION: STORE RECEIVE DATA FROM HUB")
    test_connection()
    inserted_data = []

    async def insert_data(data):
        with engine.connect() as conn:
            for item in data:
                query = insert(processed_agent_data).values(
                    road_state=item.road_state,
                    x=item.agent_data.accelerometer.x,
                    y=item.agent_data.accelerometer.y,
                    z=item.agent_data.accelerometer.z,
                    latitude=item.agent_data.gps.latitude,
                    longitude=item.agent_data.gps.longitude,
                    timestamp=item.agent_data.timestamp
                ).returning(*processed_agent_data.c)

                result = conn.execute(query)
                inserted_data.extend(result.fetchall())
            conn.commit()

    await send_data_to_subscribers(data)
    # await insert_data(data)
    print("ACTION: STORE SAVES DATA TO DB")

    if not inserted_data:
        raise HTTPException(status_code=500, detail="Failed to insert data into the database")

    return { "success": True }


@app.get("/processed_agent_data/{processed_agent_data_id}",response_model=ProcessedAgentDataInDB)
def read_processed_agent_data(processed_agent_data_id: int):
    # Get data by id
    query = processed_agent_data.select().where(processed_agent_data.c.id == processed_agent_data_id)
    with engine.connect() as conn:
        result = conn.execute(query).first()
        if result:
            return result
        else:
            raise HTTPException(status_code=404, detail="Item not found")

@app.get("/processed_agent_data/",response_model=list[ProcessedAgentDataInDB])
def list_processed_agent_data():
    # Get list of data
    query = processed_agent_data.select()
    with engine.connect() as conn:
        result = conn.execute(query).fetchall()
        return result

@app.put("/processed_agent_data/{processed_agent_data_id}")
def update_processed_agent_data(processed_agent_data_id: int, data: ProcessedAgentData):
    # Check exists
    query = processed_agent_data.select().where(processed_agent_data.c.id == processed_agent_data_id)
    with engine.connect() as conn:
        result = conn.execute(query).first()
        if not result:
            raise HTTPException(status_code=404, detail="Item not found")

    
    # Update data
    query = processed_agent_data.update().where(processed_agent_data.c.id == processed_agent_data_id).values(
        road_state=data.road_state,
        x=data.agent_data.accelerometer.x,
        y=data.agent_data.accelerometer.y,
        z=data.agent_data.accelerometer.z,
        latitude=data.agent_data.gps.latitude,
        longitude=data.agent_data.gps.longitude,
        timestamp=data.agent_data.timestamp
    )
    with engine.connect() as conn:
        conn.execute(query)
        conn.commit()
    return data

@app.delete("/processed_agent_data/{processed_agent_data_id}")
def delete_processed_agent_data(processed_agent_data_id: int):
    # Delete by id
    query = processed_agent_data.delete().where(processed_agent_data.c.id == processed_agent_data_id)
    with engine.connect() as conn:
        result = conn.execute(query)
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        conn.commit()
        return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)