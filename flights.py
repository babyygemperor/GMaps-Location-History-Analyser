import json
from dateutil.parser import parse
from math import radians, cos, sin, asin, sqrt


def read_location_history(file):
    with open(file) as f:
        data = json.load(f)
    return data['locations']


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees)
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r


def get_routes(locations):
    routes = []
    for location in locations:
        timestamp = parse(location['timestamp'])
        latitude = location['latitudeE7'] / 1E7
        longitude = location['longitudeE7'] / 1E7
        routes.append({
            'timestamp': timestamp,
            'latitude': latitude,
            'longitude': longitude,
        })
    return routes


def calculate_velocity(point1, point2):
    # calculate the distance between two points
    distance = haversine(point1['longitude'], point1['latitude'], point2['longitude'], point2['latitude'])
    # calculate the time difference in seconds
    time_diff = (point2['timestamp'] - point1['timestamp']).total_seconds()
    if time_diff > 0:
        return distance / time_diff
    else:
        return 0


def calculate_average_velocity(flight):
    total_distance = compute_flight_distance(flight)
    total_time = (flight[-1]['timestamp'] - flight[0]['timestamp']).total_seconds()
    # calculate average velocity in km/hr
    average_velocity = (total_distance / total_time) * 3600 if total_time > 0 else 0
    return average_velocity


def identify_flights(routes):
    flights = []
    flight = []

    for i in range(1, len(routes)):
        # calculate distance and time difference
        distance = haversine(routes[i - 1]['longitude'], routes[i - 1]['latitude'], routes[i]['longitude'],
                             routes[i]['latitude'])
        time_diff = (routes[i]['timestamp'] - routes[i - 1]['timestamp']).total_seconds()

        # ensure the distance and time are non-zero
        if distance > 0 and time_diff > 0:
            # calculate velocity in km/hr
            velocity = (distance / time_diff) * 3600

            # check if velocity is less than speed of sound and greater than 250 km/hr
            if 250 < velocity <= 1800:
                # add point to flight
                if len(flight) == 0:
                    flight.append(routes[i - 1])
                flight.append(routes[i])
            elif velocity < 40 and len(flight) > 0:
                # add flight to flights and reset flight if average velocity is less than 40 km/hr
                # but only if the flight distance and duration is greater than zero
                flight_distance = compute_flight_distance(flight)
                flight_duration = (flight[-1]['timestamp'] - flight[0]['timestamp']).total_seconds()
                if flight_distance > 0 and flight_duration > 0:
                    flights.append(flight)
                flight = []
    # Add the last flight if any and ensure that flight duration and distance is greater than zero
    if flight:
        flight_distance = compute_flight_distance(flight)
        flight_duration = (flight[-1]['timestamp'] - flight[0]['timestamp']).total_seconds()
        if flight_distance > 0 and flight_duration > 0:
            flights.append(flight)

    # Filter out the flights with distance less than 50 km or distance greater than 50 km but average velocity less
    # than 250 km/hr
    flights = [flight for flight in flights if
               compute_flight_distance(flight) > 200 and calculate_average_velocity(flight) >= 250]
    return flights


def compute_flight_distance(flight):
    distance = 0
    for i in range(1, len(flight)):
        lon1, lat1 = flight[i - 1]['longitude'], flight[i - 1]['latitude']
        lon2, lat2 = flight[i]['longitude'], flight[i]['latitude']
        distance += haversine(lon1, lat1, lon2, lat2)
    return distance


def main():
    file = 'Records.json'
    locations = read_location_history(file)
    routes = get_routes(locations)
    flights = identify_flights(routes)
    for flight in flights:
        start_time = flight[0]['timestamp']
        end_time = flight[-1]['timestamp']
        duration = end_time - start_time
        distance = compute_flight_distance(flight)
        print(
            f"Flight on date: {start_time.date()}, time: {str(start_time.time())[:8]}-{str(end_time.time())[:8]} "
            f"from {flight[0]['latitude']}, {flight[0]['longitude']} to {flight[-1]['latitude']}, "
            f"{flight[-1]['longitude']}. Duration: {duration}, Distance: {distance} km")


if __name__ == "__main__":
    main()
