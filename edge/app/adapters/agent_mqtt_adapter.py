import paho.mqtt.client as mqtt
from abc import ABC, abstractmethod
from app.interfaces.agent_gateway import AgentGateway

class AgentMQTTAdapter(AgentGateway):
    def __init__(self, broker_host, broker_port, topic, hub_gateway):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topic = topic
        self.hub_gateway = hub_gateway
        self.client = mqtt.Client()

    def on_message(self, client, userdata, msg):
        """
        Handle incoming messages from the agent.
        """
        try:
            payload = json.loads(msg.payload.decode('utf-8'))
            accelerometer_data = payload['accelerometer']
            gps_data = payload['gps']
            timestamp = payload['timestamp']

            agent_data = AgentData(
                accelerometer=accelerometer_data,
                gps=gps_data,
                timestamp=timestamp
            )

            processed_data = process_agent_data(agent_data)

        except Exception as e:
            print(f"Error processing message: {e}")

    def connect(self):
        """
        Establish a connection to the agent.
        """
        self.client.connect(self.broker_host, self.broker_port)

    def start(self):
        """
        Start listening for messages from the agent.
        """
        self.client.on_message = self.on_message
        self.client.subscribe(self.topic)
        self.client.loop_start()

    def stop(self):
        """
        Stop the agent gateway and clean up resources.
        """
        self.client.loop_stop()
        self.client.disconnect()