import pandas as pd

def load_data(file_path):
    """Load data from a CSV file."""
    try:
        
        stops = pd.read_csv(file_path + 'stops.txt')
        stop_times = pd.read_csv(file_path + 'stop_times.txt')
        routes = pd.read_csv(file_path + 'routes.txt')
        trips = pd.read_csv(file_path + 'trips.txt')

        data = [stops, stop_times, routes, trips]

        print("Data loaded successfully.")
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def get_all_stops_by_trip_id(trips, stops, stop_times, trip_id):
    """Get all stops for a given trip ID."""
    try:
        stop_times_info = stop_times[stop_times['trip_id'] == trip_id].sort_values('departure_time').merge(stops, on='stop_id', how='left')
        result = stop_times_info[['stop_name', 'arrival_time', 'departure_time', 'platform_code']]
        return result
    except Exception as e:
        print(f"Error retrieving stops for trip ID {trip_id}: {e}")
        return None
    
def get_trip_info(trips, routes, calendar, calendar_dates, trip_id):
    """Get trip information for a given trip ID."""
    try:
        trip_info = trips[trips['trip_id'] == trip_id].merge(routes, on='route_id', how='left')
        
        return trip_info
    except Exception as e:
        print(f"Error retrieving trip info for trip ID {trip_id}: {e}")
        return None

if __name__ == "__main__":
    file_path = 'dataset/google_transit/'
    data = load_data(file_path)

    if data is not None:
        stops, stop_times, routes, trips = data

        print(stops.head())
        print(stop_times.head())
        print(routes.head())
        print(trips.head())

        filtered_stops = stops[stops['stop_name'].str.contains('Wrocław|Iwiny', case=False, na=False)]

        print(get_all_stops_by_trip_id(trips, stops, stop_times, '37148498_396994'))

