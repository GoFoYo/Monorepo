from csv import reader
from datetime import datetime
from domain.aggregated_data import AggregatedData, Accelerometer, Gps
from domain.parking import Parking

class FileDatasource:
    def __init__(self, accelerometer_filename: str, gps_filename: str, parking_filename:str) -> None:
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename
        self.parking_filename = parking_filename
        self.accelerometer_data = None  
        self.gps_data = None
        self.parking_data = None
        self.is_reading_finished = False
        self.iteration = 0
        
    def isReadingFinished(self) -> bool:
        """Метод повертає True якщо читання даних завершено"""
        return self.is_reading_finished

    def read(self) -> tuple[AggregatedData, Parking]:
        """Метод повертає дані отримані з датчиків"""
        if (self.iteration == 0):
            self.startReading()
            
        self.iteration += 1
        accelerometer = self._get_next_or_none(self.accelerometer_data)
        gps = self._get_next_or_none(self.gps_data)
        parking = self._get_next_or_none(self.parking_data)

        if (all(schema is None for schema in [accelerometer, gps, parking])):
          self.stopReading()

        return AggregatedData(
                accelerometer=self._get_next_or_none(self.accelerometer_data), 
                gps=self._get_next_or_none(self.gps_data), 
                time=datetime.now()
            ), self._get_next_or_none(self.parking_data)

    def startReading(self, *args, **kwargs):
        """Метод повинен викликатись перед початком читання даних"""
        self.accelerometer_data = self._read_accelerometer_data()
        self.gps_data = self._read_gps_data()
        self.parking_data = self._read_parking_data()
        self.is_reading_finished = False

    def stopReading(self, *args, **kwargs):
        """Метод повинен викликатись для закінчення читання даних"""
        self.is_reading_finished = True
    
    def _get_next_or_none(self, iterator):
        try:
            return next(iterator)
        except StopIteration:
            return None

    def _read_accelerometer_data(self):
        with open(self.accelerometer_filename, 'r') as file:
            csv_reader = reader(file)
            next(csv_reader) 
            data = [tuple(map(int, row)) for row in csv_reader]
            
            for point in data:
              yield Accelerometer(*point)

    def _read_gps_data(self):
        with open(self.gps_filename, 'r') as file:
            csv_reader = reader(file)
            next(csv_reader)  
            data = [tuple(map(float, row)) for row in csv_reader]

            for point in data:
              yield Gps(*point)

    def _read_parking_data(self):
        with open(self.parking_filename, 'r') as file:
            csv_reader = reader(file)
            next(csv_reader)  
            data = [tuple(map(float, row)) for row in csv_reader]

            for empty_count, longitude, latitude in data:
              yield Parking(empty_count, Gps(longitude, latitude))
