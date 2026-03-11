import pandas as pd
from helper import time_to_seconds, get_time_diff

class RideController:

    def load_data(self):
        
        self.stops = pd.read_csv(self.path_to_gtfs + 'stops_with_cities.txt')
        self.stop_times = pd.read_csv(self.path_to_gtfs + 'stop_times.txt')
        self.routes = pd.read_csv(self.path_to_gtfs + 'routes.txt')
        self.trips = pd.read_csv(self.path_to_gtfs + 'trips.txt')
        self.calendar = pd.read_csv(self.path_to_gtfs + 'calendar.txt')
        self.calendar_dates = pd.read_csv(self.path_to_gtfs + 'calendar_dates.txt')

        print("GTFS data loaded successfully.")

    def load_cities_data(self):
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

        df_cities = pd.read_csv(self.path_to_cities, sep='\t', header=None, names=column_names, dtype=dtype_settings, low_memory=False)
        final_cities = df_cities[(df_cities['feature_code'].isin(valid_city_codes))]
        final_cities = final_cities.sort_values('population', ascending=False)

        self.cities = final_cities[['geonameid', 'name', 'latitude', 'longitude', 'population']]

        print("Cities data loaded successfully.")

    def get_service_ids_on_date(self, date):

        sevice_ids_on_date = set()
        search_date_int = int(date)

        date_dt = pd.to_datetime(date, format='%Y%m%d')
        day_name = date_dt.day_name().lower()

        print(date_dt, ' - ', day_name)

        mask = (
            (self.calendar[day_name] == 1) & 
            (self.calendar['start_date'].astype(int) <= search_date_int) & 
            (self.calendar['end_date'].astype(int) >= search_date_int)
        )
        service_ids = set(self.calendar.loc[mask, 'service_id'])

        if self.calendar_dates is not None and not self.calendar_dates.empty:
            cd = self.calendar_dates
            cd_date_int = cd['date'].astype(int)

            added = cd[(cd_date_int == search_date_int) & (cd['exception_type'] == 1)]
            service_ids.update(added['service_id'])

            removed = cd[(cd_date_int == search_date_int) & (cd['exception_type'] == 2)]
            service_ids.difference_update(removed['service_id'])

        return service_ids

    def find_next_stops(self, start_stop_id, date, time, max_time = 3600*16):
        # Implementacja wyszukiwania po dacie i przystanku początkowym

        service_ids = self.get_service_ids_on_date(date)
        trips_on_date = self.trips[self.trips['service_id'].isin(service_ids)]

        stop_times_on_date = self.stop_times[self.stop_times['trip_id'].isin(trips_on_date['trip_id'])]
        stop_times_from_start_stop = stop_times_on_date[stop_times_on_date['stop_id'] == start_stop_id]

        filtered_stop_times = stop_times_from_start_stop[stop_times_from_start_stop['departure_time'].apply(lambda x: time_to_seconds(x) >= time_to_seconds(time) and time_to_seconds(x) <= time_to_seconds(time) + max_time)].join(self.stops.set_index('stop_id'), on='stop_id', how='left', rsuffix='_stop')

        for _, row in filtered_stop_times.iterrows():

            next_stops_on_trip = stop_times_on_date[
                (stop_times_on_date['trip_id'] == row['trip_id']) & 
                (stop_times_on_date['stop_sequence'] > row['stop_sequence'])
            ].join(self.stops.set_index('stop_id'), on='stop_id', how='left', rsuffix='_stop').sort_values('stop_sequence')

            if not next_stops_on_trip.empty:
                # Nagłówek kursu (oddzielony linią dla przejrzystości)
                print("\n" + "="*80)
                print(f"TRASA DLA KURSU ID: {row['trip_id']}")
                print("-"*80)
                
                print(f"START  | {row['departure_time'][:5]:<14} | {get_time_diff(time, row['departure_time']):<6} | {row['stop_name']}")

                for _, next_stop in next_stops_on_trip.iterrows():
                    arr = next_stop['arrival_time'][:5]
                    dep = next_stop['departure_time'][:5]
                    
                    time_display = f"{arr}" if arr == dep else f"{arr} -> {dep}"
                    
                    print(f"       | {time_display:<14} | {get_time_diff(time, next_stop['arrival_time']):<6} | {next_stop['stop_name']}")

                print("="*80)

    def find_connections_by_date_and_start_stop(self, start_stop_id, date, time, max_time = 3600):
        # Implementacja wyszukiwania po dacie i przystanku początkowym
        pass

    def __init__(self, path_to_gtfs, path_to_cities):
        self.path_to_gtfs = path_to_gtfs
        self.path_to_cities = path_to_cities

        self.load_data()
        self.load_cities_data()

if __name__ == "__main__":
    path_to_gtfs = "gtfs_generic_eu/"
    path_to_cities = "cities15000.txt"

    controller = RideController(path_to_gtfs, path_to_cities)

    controller.find_next_stops(start_stop_id='dcc29016-9603-11e6-9066-549f350fcb0c', date="20260702", time="08:00:00")

