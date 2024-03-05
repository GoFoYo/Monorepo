from paho.mqtt import client as mqtt_client
import time
from schema.aggregated_data_schema import AggregatedDataSchema
from schema.parking_schema import ParkingSchema
from file_datasource import FileDatasource
import config

def connect_mqtt(broker, port):
  """Create MQTT client"""
  print(f"CONNECT TO {broker}:{port}")

  def on_connect(client, userdata, flags, rc):
    if rc == 0:
      print(f"Connected to MQTT Broker ({broker}:{port})!")
    else:
      print("Failed to connect {broker}:{port}, return code %d\n", rc)
      exit(rc) # Stop execution
  
  client = mqtt_client.Client()
  client.on_connect = on_connect
  client.connect(broker, port)
  client.loop_start()
  
  return client

def publish(client, topic, parking_topic, datasource, delay):
  datasource.startReading()
  
  while not datasource.isReadingFinished():
    time.sleep(delay)
    data, parking_data = datasource.read()
    print(f"Data: {data}")
    print(f"Parking: {parking_data}")
    msg = AggregatedDataSchema().dumps(data)
    parking_msg = ParkingSchema().dumps(parking_data)
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    
    # if status == 0:
    #   print(f"Send `{msg}` to topic `{topic}`")
    # else:
    #   print(f"Failed to send message to topic {topic}")

    result = client.publish(parking_topic, parking_msg)
    status = result[0]
    # if status == 0:
    #   print(f"Send `{parking_msg}` to topic `{parking_topic}`")
    # else:
    #   print(f"Failed to send message to topic {parking_topic}")

def run():
  # Prepare mqtt client
  client = connect_mqtt(config.MQTT_BROKER_HOST, config.MQTT_BROKER_PORT)
  # Prepare datasource
  datasource = FileDatasource("data/accelerometer.csv", "data/gps.csv", "data/parking.csv")
  # Infinity publish data
  publish(client, config.MQTT_TOPIC, config.MQTT_PARKING_TOPIC, datasource, config.DELAY)

if __name__ == '__main__':
  run()