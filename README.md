# Google Maps Location History Distance Calculator

This application is a Flask-based web service for calculating the distance travelled based on Google Maps Location History data. It accepts a JSON file of your location history data exported from Google, along with the start and end dates to calculate the distance covered in that period. The distance covered is also represented as the number of times around the Earth and the number of trips to the Moon. Moreover, a heatmap of the visited locations is displayed on the interface.

**Note: You need your Google Maps Location History Export for this to work**

## Features
- Calculates distance travelled based on location history
- Visualizes visited locations on a heatmap
- Calculates and shows how many times around the Earth and to the Moon the distance covered represents
- Supports localization of data timestamps to UTC timezone

## Requirements
- Flask
- Flask-CORS
- haversine
- pytz
- json
- datetime
- dateutil
- statistics

## Setup and Installation
1. Ensure that you have Python 3.6 or later installed on your system.

2. Clone this repository to your local machine:
    ```sh
    git clone https://github.com/babyygemperor/GMaps-Location-History-Analyser.git
    ```

3. Navigate to the cloned directory:
    ```sh
    cd GMaps-Location-History-Analyser
    ```

4. Install the required packages:
    *I was too lazy to write a requirements.txt*

5. Run the application:
    ```sh
    python main.py
    ```

6. Open a web browser and navigate to `http://localhost:5000` to use the application.

## How to use
1. Navigate to `http://localhost:5000` in your web browser.

2. In the form displayed, select the start and end dates for the period you wish to calculate the distance for. You can also set the end date to today's date by clicking the "Set end date to today" button.

3. Click the "Select JSON file" field and select the Google Maps Location History JSON file from your system.

4. Click the "Calculate Distance" button. 

5. The application will display the total distance travelled, the equivalent number of times around the Earth and to the Moon, and a heatmap of the visited locations during the selected period.


# flights.py

The given Python script identifies flights in a person's location history data, calculates various attributes of these flights (such as the start time, end time, duration, distance, and average speed), and prints out a summary of each flight. 

## Requirements

Python 3.x is required to run this script. 

It also depends on the following Python packages:

- `requests`
- `dateutil`
- `math`
- `json`

These packages can be installed using pip:

```bash
pip install requests python-dateutil
```

## Inputs

The main input for this script is a `JSON` file that contains a person's location history data. This file is structured as an array of location objects, each of which has a `timestamp`, `latitudeE7`, and `longitudeE7` fields.

Here is a sample `JSON` file:

```json
{
  "locations": [
    {
      "timestamp": "2023-01-01T00:00:00Z",
      "latitudeE7": 523456789,
      "longitudeE7": -23456789
    },
    ...
  ]
}
```

## Outputs

The script prints a summary of each identified flight to the console. Here is a sample output:

```
Flight on date: 2023-01-01, time: 00:00:00-02:00:00 from Airport1 to Airport2. Duration: 2:00:00, Distance: 1000.00 km, Speed: 500.00 km/hr
...
```

## Functionality

Here is a brief overview of the main functions in the script:

- `read_location_history(file)`: Reads location history data from a file.
- `haversine(lon1, lat1, lon2, lat2)`: Calculates the distance between two points on the Earth.
- `get_routes(locations)`: Converts location data into routes.
- `calculate_velocity(point1, point2)`: Calculates the velocity between two points.
- `calculate_average_velocity(flight)`: Calculates the average velocity of a flight.
- `merge_flights(flights, speed_tolerance=50, time_gap=30)`: Merges flights that are close in time and have similar speeds.
- `identify_flights(routes)`: Identifies flights from a list of routes.
- `compute_flight_distance(flight)`: Computes the total distance of a flight.
- `get_city_name(lat, long)`: Retrieves the city name for a given latitude and longitude.
- `find_nearest_airport(lat, lon)`: Finds the nearest airport to a given latitude and longitude.

The `main` function ties everything together: it reads location history data from a file, identifies flights, and prints out a summary of each flight.

## How to Run

To run this script, you need to replace the username with your GeoNames username in the `find_nearest_airport` function. Then, replace `'Records.json'` with the path to your location history file in the `main` function. 

After these modifications, you can run the script from the command line:

```bash
python flights.py
```



## Contribution
Contributions, issues, and feature requests are welcome. Feel free to check the [issues page](https://github.com/babyygemperor/GMaps-Location-History-Analyser/issues) if you want to contribute.

## License
This project is [MIT](https://choosealicense.com/licenses/mit/) licensed.
