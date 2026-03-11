import pandas as pd
import numpy as np
from helper import normalize_text, get_distance, EARTH_RADIUS
from cities_assigner import get_cities_info
import sys

def load_data(file_path):
    """Load data from a CSV file."""
    try:
        
        stops = pd.read_csv(file_path + 'stops_with_cities.txt')
        stop_times = pd.read_csv(file_path + 'stop_times.txt')
        routes = pd.read_csv(file_path + 'routes.txt')
        trips = pd.read_csv(file_path + 'trips.txt')

        data = [stops, stop_times, routes, trips]

        print("Data loaded successfully.")
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def get_all_stops_by_coordinates(stops, cities, longitude, latitude, radius):
    """Pobiera wszystkie przystanki w promieniu podanym w kilometrach."""
    try:
        R = EARTH_RADIUS

        lat1 = np.radians(latitude)
        lon1 = np.radians(longitude)
        lat2 = np.radians(stops['stop_lat'])
        lon2 = np.radians(stops['stop_lon'])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        
        stops['distance'] = R * c
        
        nearby_stops = stops[stops['distance'] <= radius].join(cities.set_index('geonameid'), on='city_id', how='left', rsuffix='_city')
        
        return nearby_stops[['stop_id', 'name', 'stop_name', 'stop_lon', 'stop_lat', 'distance']].sort_values('distance')
        
    except Exception as e:
        print(f"Error retrieving stops by coordinates: {e}")
        return None
    
def get_all_cities_by_coordinates(cities, longitude, latitude, radius):
    """Pobiera wszystkie miasta w promieniu podanym w kilometrach."""
    try:
        R = EARTH_RADIUS

        lat1 = np.radians(latitude)
        lon1 = np.radians(longitude)
        lat2 = np.radians(cities['latitude'])
        lon2 = np.radians(cities['longitude'])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        
        cities['distance'] = R * c
        
        nearby_cities = cities[cities['distance'] <= radius]

        return nearby_cities[['name', 'longitude', 'latitude', 'distance']].sort_values('distance')

        
    except Exception as e:
        print(f"Error retrieving cities by coordinates: {e}")
        return None

def find_stops_near_city(stops, cities, city_name, radius):
    search_name = normalize_text(city_name)
    cities_temp = cities.copy()
    cities_temp['name_normalized'] = cities_temp['name'].apply(normalize_text)
    
    cities_temp = cities_temp.sort_values('population', ascending=False)
    
    city_match = cities_temp[cities_temp['name_normalized'] == search_name]

    if city_match.empty:
        city_match = cities_temp[cities_temp['name_normalized'].str.contains(search_name, na=False)]
        
    if city_match.empty:
        print(f"City '{city_name}' (normalized: '{search_name}') not found.")
        return None
    
    city = city_match.iloc[0]
    city_lon = city['longitude']
    city_lat = city['latitude']
    
    print(f"Found city: {city['name_normalized']} (Pop: {city['population']})")
    nearby_stops = get_all_stops_by_coordinates(stops, cities, city_lon, city_lat, radius)
    return nearby_stops

def main():
    if len(sys.argv) < 3:
        print("Użycie: python flixbus.py <miasto> <promień>")
        print("Przykład: python flixbus.py Lviv 100")
        return

    city_name = sys.argv[1]
    try:
        radius = float(sys.argv[2])
    except ValueError:
        print("Błąd: Promień musi być liczbą.")
        return

    file_path = "gtfs_generic_eu/"

    print(f"Loading data and searching for {city_name} within {radius} km...")
    
    data = load_data(file_path)
    cities = get_cities_info('cities15000.txt')

    if data is not None:
        stops, stop_times, routes, trips = data
        nearby_stops = find_stops_near_city(stops, cities, city_name, radius)
        
        if nearby_stops is not None and not nearby_stops.empty:
            print(f"\nStops near {city_name} within {radius} km:")
            print(nearby_stops)
        else:
            print(f"No stops found near {city_name}.")

if __name__ == "__main__":
    main()