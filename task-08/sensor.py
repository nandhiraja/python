import asyncio
import random
from datetime import datetime

async def sensor_stream(sensor_id: str = "sensor-T1"):
    """
    Simulates a live IoT sensor feed emitting data every second.
    Normally generates temperatures around 70-80F.
    Periodically simulates a spike (anomaly) > 100F.
    """
    base_temp = 75.0
    base_vib = 0.1
    
    counter = 0

    while True:
        # Simulate an anomaly every ~30 seconds
        is_anomaly = (counter % 30) >= 27
        
        if is_anomaly:
            temp = base_temp + random.uniform(25.0, 35.0)
            vib = base_vib + random.uniform(0.3, 0.6)
        else:
            temp = base_temp + random.uniform(-5.0, 5.0)
            vib = base_vib + random.uniform(-0.05, 0.05)
            
        # Ensure values don't go negative on vibration
        vib = max(0.0, vib)
        
        data_point = {
            "timestamp": datetime.now().isoformat(),
            "sensor_id": sensor_id,
            "temperature": round(temp, 1),
            "vibration": round(vib, 2)
        }
        
        yield data_point
        counter += 1
        await asyncio.sleep(1)
