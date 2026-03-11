import pandas as pd
from bisect import bisect_left
from helper import normalize_text

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

def get_cities_info(path):
    column_names = [
        'geonameid', 'name', 'asciiname', 'alternatenames', 
        'latitude', 'longitude', 'feature_class', 'feature_code', 
        'country_code', 'cc2', 'admin1_code', 'admin2_code', 
        'admin3_code', 'admin4_code', 'population', 'elevation', 
        'dem', 'timezone', 'modification_date'
    ]

    dtype_settings = {
        'cc2': str,
        'admin1_code': str,
        'admin2_code': str,
        'admin3_code': str,
        'admin4_code': str
    }

    valid_city_codes = ['PPLC', 'PPLA', 'PPLA2', 'PPLA3', 'PPL']

    df_cities = pd.read_csv(path, sep='\t', header=None, names=column_names, dtype=dtype_settings, low_memory=False)
    final_cities = df_cities[(df_cities['feature_code'].isin(valid_city_codes))]
    final_cities = final_cities.sort_values('population', ascending=False)

    return final_cities[['geonameid', 'name', 'latitude', 'longitude', 'population']]

def assign_city_to_stop_optimized(stops, cities, offset=50):
    """
    Szybkie przypisanie miasta przy użyciu okna wyszukiwania 
    w posortowanych współrzędnych.
    """

    # 1. Sortujemy miasta po długości geograficznej
    cities_sorted = cities.sort_values('longitude').reset_index(drop=True)
    lons = cities_sorted['longitude'].values
    cities_by_population = cities.sort_values('population', ascending=False)
    cities_by_population['name'] = cities_by_population['name'].apply(normalize_text)
    
    results = []

    for _, stop in stops.iterrows():

        stop_city_prefix = stop['stop_name'].split(',')[0].strip()

        if stop_city_prefix:
            city_match = cities_by_population[cities_by_population['name'].str.lower() == stop_city_prefix.lower()]
            if not city_match.empty:
                results.append(city_match.iloc[0]['geonameid'])
                continue

        s_lon = stop['stop_lon']
        s_lat = stop['stop_lat']
        
        # 2. Znajdujemy punkt wstawienia (najbliższy indeks dla longitude)
        idx = bisect_left(lons, s_lon)
        
        # 3. Definiujemy "okno" (kilka miast w lewo i w prawo od indeksu)
        start = max(0, idx - offset)
        end = min(len(cities_sorted), idx + offset)
        
        # Pobieramy tylko tych kilku kandydatów
        candidates = cities_sorted.iloc[start:end].copy()
        
        # 4. Liczymy dystans tylko dla tych kilku miast
        candidates['dist'] = ((candidates['longitude'] - s_lon)**2 + 
                             (candidates['latitude'] - s_lat)**2)**0.5
        
        closest = candidates.loc[candidates['dist'].idxmin()]
        results.append(closest['geonameid'])
    
    stops['city_id'] = results
    return stops

def save_all_stops(stops, path):
    stops.to_csv(path, index=False)

if __name__ == "__main__":
    file_path = "gtfs_generic_eu/"
    print("Loading data...")
    data = load_data(file_path)
    cities = get_cities_info('cities15000.txt')

    if data is not None:
        stops, stop_times, routes, trips = data

        stops = assign_city_to_stop_optimized(stops, cities)

        print(stops.head())
        save_all_stops(stops, "gtfs_generic_eu/stops_with_cities.txt")