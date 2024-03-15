import asyncio
import csv
import scipy.signal
import websockets
import time
import json
from kivy.app import App
from kivy_garden.mapview import MapMarker, MapView
from kivy.clock import Clock
from lineMapLayer import LineMapLayer
from datasource import Datasource
from entities.processed_agent_data import ProcessedAgentData

data_file = "./data.csv"
gps_file = "./gps.csv"
API_URL = "ws://localhost:8000/ws/"

def push_data(mapViewApp, data):
    z_values = [processed_agent_data.agent_data.accelerometer.z for processed_agent_data in data if processed_agent_data.agent_data is not None]
    gps_data_array = [
    [processed_agent_data.agent_data.gps.longitude, processed_agent_data.agent_data.gps.latitude]
        for processed_agent_data in data if processed_agent_data.agent_data is not None
    ]
    
    mapViewApp.data_array.extend(z_values)
    filtered_array = [arr for arr in gps_data_array if arr != [0, 0]]
    mapViewApp.gps_array.extend(filtered_array)

async def connect_websocket(mapViewApp):
    async with websockets.connect(API_URL) as websocket:
        while True:
            data = await websocket.recv()
            parsed_data_array = json.loads(data)
            result = []
            for parsed_data in parsed_data_array:
                received_obj = ProcessedAgentData(**parsed_data)  # Unpack dictionary into object
                result.append(received_obj)
            push_data(mapViewApp, result)


class MapViewApp(App):
    def __init__(self, **kwargs):
        super().__init__()
        self.car_marker = None

        self.map = LineMapLayer()
        self.data_array = [] # only z coordinate from accelerometer
        self.gps_array = [] # [[1,2], [3,4]]
        self.data_peaks = []
    
    def on_start(self):
        Clock.schedule_interval(self.update, 1 / 100.0)

    def update(self, *args):
        if(len(self.gps_array) == 0):
            return

        self.update_car_marker(self.gps_array[len(self.gps_array)-1])
        if len(self.data_array) > 30:
            self.check_road_quality()
            self.data_array = []
            self.gps_array = []

    def check_road_quality(self):
        bumps, _ = scipy.signal.find_peaks(self.data_array, prominence=7000, width=3)
        potholes, _ = scipy.signal.find_peaks([-1 * i for i in self.data_array], prominence=7000, width=3)
        for i in range(len(bumps)):
            self.set_bump_marker(self.gps_array[bumps[i]])
        for i in range(len(potholes)):
            self.set_pothole_marker(self.gps_array[potholes[i]])

    def update_car_marker(self, point):
        if self.car_marker:
            self.car_marker.detach()
        
        self.car_marker = MapMarker(lat=point[0], lon=point[1], source='images/car.png')
        self.mapview.add_marker(self.car_marker)
        self.mapview.center_on(point[0], point[1])

    def set_pothole_marker(self, point):
        self.mapview.add_marker(
            MapMarker(lat=point[0], lon=point[1], source='images/pothole.png')
        )


    def set_bump_marker(self, point):
        self.mapview.add_marker(
            MapMarker(lat=point[0], lon=point[1], source='images/bump.png')
        )

    def build(self):
        self.mapview = MapView(zoom=12, lat=50.4501, lon=30.5234)
        self.mapview.add_layer(self.map)
        return self.mapview


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    mapViewApp = MapViewApp()
    # asyncio.run(connect_websocket(mapViewApp))
    # Clock.schedule_interval(self.update, 1 / 100.0)
    loop.run_until_complete(
        asyncio.gather(
            connect_websocket(mapViewApp),
            mapViewApp.async_run(async_lib="asyncio")
            )
        )
    loop.close()
