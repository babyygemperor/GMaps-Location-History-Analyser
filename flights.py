import json
import requests

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


def merge_flights(flights, speed_tolerance=50, time_gap=30):
    merged_flights = []
    current_flight = flights[0]
    merged_flights.append(current_flight)

    for i in range(len(flights) - 1):
        next_flight = flights[i + 1]
        if should_merge(current_flight, next_flight, speed_tolerance, time_gap):
            for flight in next_flight:
                current_flight.append(flight)
        else:
            merged_flights.append(current_flight)
            current_flight = next_flight
    merged_flights.append(flights[-1])
    return merged_flights


def should_merge(flight1, flight2, speed_tolerance=50, time_gap=30):
    # Parse end time of flight1 and start time of flight2
    end_time_flight1 = flight1[-1]['timestamp']
    start_time_flight2 = flight2[0]['timestamp']

    # Calculate the time difference in minutes
    time_diff = (start_time_flight2 - end_time_flight1).total_seconds() / 60

    # Compare the speeds of the flights
    speed_diff = abs(
        (compute_flight_distance(flight1) / (flight1[-1]['timestamp'] - flight1[0]['timestamp']).total_seconds()) - (
                compute_flight_distance(flight2) / (
            (flight2[-1]['timestamp'] - flight2[0]['timestamp']).total_seconds())))

    # Decide if the flights should be merged
    if time_diff <= time_gap and speed_diff <= speed_tolerance:
        return True

    return False


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

    # Filter out the flights with distance less than 200 km or distance greater than 200 km but average velocity less
    # than 250 km/hr
    flights = merge_flights(flights)
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
            f"from {find_nearest_airport(flight[0]['latitude'], flight[0]['longitude'])} to "
            f"{find_nearest_airport(flight[-1]['latitude'], flight[-1]['longitude'])}."
            f"Duration: {duration}, Distance: {round(distance, 2)} km, "
            f"Speed: {round(distance / duration.total_seconds() * 3600, 2)}")


def get_city_name(lat, long):
    headers = {"accept-language": "en"}
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={long}"
    response = requests.get(url, headers=headers)
    data = response.json()
    if 'address' in data and 'city' in data['address']:
        return data['address']['city']
    elif 'address' in data and 'town' in data['address']:
        return data['address']['town']
    elif 'address' in data and 'village' in data['address']:
        return data['address']['village']
    else:
        return "Location not identified"


def find_nearest_airport(lat, lon):
    username = "aamingem"  # Replace with your GeoNames username
    url = f"http://api.geonames.org/findNearbyJSON?lat={lat}&lng={lon}&fcode=AIRP&username={username}"

    response = requests.get(url)
    data = response.json()

    if len(data['geonames']) == 0:
        return f"{lat}, {lon}"
    if 'geonames' in data and len(data['geonames']) > 0:
        return data['geonames'][0]['name']
    else:
        return f"{data['geonames'][0]['lat']}, {data['geonames'][0]['lng']}"


if __name__ == "__main__":
    main()
