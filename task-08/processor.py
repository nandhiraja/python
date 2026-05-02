import pandas as pd
from collections import deque
from datetime import datetime

class StreamProcessor:
    def __init__(self, window_size=300):
        self.window_size = window_size
        self.data_queue = deque(maxlen=window_size)
        self.temp_threshold = 100.0

    def process_point(self, data_point: dict) -> dict:
        
        self.data_queue.append({
            "timestamp": datetime.fromisoformat(data_point["timestamp"]),
            "temperature": data_point["temperature"],
            "vibration": data_point["vibration"]
        })

        df = pd.DataFrame(list(self.data_queue))
        
        current_temp = data_point["temperature"]
        current_vib = data_point["vibration"]
        
        status = "NORMAL"
        alert = None
        
        if len(df) > 1:
            mean_temp = df["temperature"].mean()
            std_temp = df["temperature"].std()
            
            if std_temp == 0:
                std_temp = 0.001
                
            z_score = (current_temp - mean_temp) / std_temp
            
            if current_temp >= self.temp_threshold:
                status = "CRITICAL"
                alert = {
                    "sensor_id": data_point["sensor_id"],
                    "current": current_temp,
                    "avg_5m": round(mean_temp, 1),
                    "sigma": round(z_score, 1),
                    "message": f"Temperature exceeded threshold (>{int(self.temp_threshold)}F)"
                }
            elif z_score > 2.0 or current_temp >= 90.0:
                status = "WARNING"
                
            result = {
                "timestamp": data_point["timestamp"],
                "sensor_id": data_point["sensor_id"],
                "temperature": current_temp,
                "vibration": current_vib,
                "moving_avg": round(mean_temp, 1),
                "z_score": round(z_score, 1),
                "status": status,
                "alert": alert
            }
        else:
            result = {
                "timestamp": data_point["timestamp"],
                "sensor_id": data_point["sensor_id"],
                "temperature": current_temp,
                "vibration": current_vib,
                "moving_avg": current_temp,
                "z_score": 0.0,
                "status": "NORMAL",
                "alert": None
            }
            
        return result
