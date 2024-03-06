from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData

def process_agent_data(
agent_data: AgentData,
) -> ProcessedAgentData:
    """
    Process agent data and classify the state of the road surface.
    Parameters:
    agent_data (AgentData): Agent data that contains accelerometer, GPS, and timestamp.
    Returns:
    processed_data (ProcessedAgentData): Processed data containing the classified state of
    the road surface and agent data.
    """
    z_value = agent_data.accelerometer.z

    if z_value < 16541 - 1500:
        road_state = "bump"
    elif z_value > 16541 + 1500:
        road_state = "pothole"
    else:
        road_state = "normal"

    processed_data = ProcessedAgentData(road_state=road_state, agent_data=agent_data)
    return processed_data