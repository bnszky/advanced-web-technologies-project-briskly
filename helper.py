import unicodedata
import numpy as np

EARTH_RADIUS = 6371.0 

def time_to_seconds(time_str):
    h, m, s = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s

def get_time_diff(start_str, end_str):
    start_sec = time_to_seconds(start_str)
    end_sec = time_to_seconds(end_str)
    
    diff_sec = end_sec - start_sec
    
    hours = diff_sec // 3600
    minutes = (diff_sec % 3600) // 60
    
    return f"{hours}:{minutes:02d}h"

def normalize_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = text.replace('ł', 'l')
    text = unicodedata.normalize('NFKD', text)
    text = "".join([c for c in text if not unicodedata.combining(c)])
    return text.lower().strip()

def get_distance(lat1, lon1, lat2, lon2):
    """Oblicza odległość między dwoma punktami geograficznymi."""
    R = EARTH_RADIUS

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    
    distance = R * c
    return distance