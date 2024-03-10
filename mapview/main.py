import asyncio
import csv
import scipy.signal

from kivy.app import App
from kivy_garden.mapview import MapMarker, MapView
from kivy.clock import Clock
from lineMapLayer import LineMapLayer
from datasource import Datasource

data_file = "./data.csv"
gps_file = "./gps.csv"


class MapViewApp(App):
    def __init__(self, **kwargs):
        super().__init__()
        self.car_marker = None

        self.map = LineMapLayer()
        self.data_array = []
        self.gps_array = []
        self.data_peaks = []

        self.emulation_data_array = []
        self.emulation_gps_array = []
        self.emulation_index = 0

    def on_start(self):
        with open(data_file, 'r') as data_reader:
            reader = csv.reader(data_reader)
            next(reader)  # skip header
            self.emulation_data_array = [int(row[2]) for row in csv.reader(data_reader)]

        with open(gps_file, 'r') as data_reader:
            reader = csv.reader(data_reader)
            next(reader)  # skip header
            self.emulation_gps_array = [[float(row[0]), float(row[1])] for row in csv.reader(data_reader)]
        # once per 10ms
        Clock.schedule_interval(self.update, 1 / 100.0)

    def update(self, *args):
        # --- Emulation ---
        self.emulation_index += 1
        if self.emulation_index < len(self.emulation_data_array):
            self.data_array.append(self.emulation_data_array[self.emulation_index])
            # should handle different data rates
            gps_index = (self.emulation_index * len(self.emulation_gps_array)) / len(self.emulation_data_array)
            self.gps_array.append(self.emulation_gps_array[int(gps_index)])
        # --- End of emulation ---
        self.update_car_marker(self.gps_array[len(self.gps_array)-1])
        if len(self.data_array) > 100:
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
    loop.run_until_complete(MapViewApp().async_run(async_lib="asyncio"))
    loop.close()
