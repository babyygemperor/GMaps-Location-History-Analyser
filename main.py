from flask import Flask, request, render_template
from haversine import haversine
import pytz
import json
import datetime
from dateutil import parser

app = Flask(__name__)


def calculate_distance(data, start_date, end_date):
    # Convert the provided dates into datetime objects
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    # Make the start and end dates timezone-aware
    utc = pytz.UTC
    start_date = utc.localize(start_date)
    end_date = utc.localize(end_date)

    total_distance = 0.0

    # Filter locations within the provided date range
    for i in range(len(data) - 1):
        timestamp = datetime.datetime.fromisoformat(data[i]['timestamp'].replace('Z', '+00:00'))

        if start_date <= timestamp <= end_date:
            lat1, lon1 = data[i]['latitudeE7'] / 1e7, data[i]['longitudeE7'] / 1e7
            lat2, lon2 = data[i + 1]['latitudeE7'] / 1e7, data[i + 1]['longitudeE7'] / 1e7

            # Skip if the current or next location is (0, 0)
            if (lat1, lon1) == (0, 0) or (lat2, lon2) == (0, 0):
                continue

            if abs(haversine((lat1, lon1), (lat2, lon2)) / (parser.parse(data[i]['timestamp']) - parser.parse(
                    data[i + 1]['timestamp'])).total_seconds() * 3600) > 1200:
                continue

            distance = haversine((lat1, lon1), (lat2, lon2))
            total_distance += distance

    return total_distance


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        file = request.files['file']

        if file:
            data = json.load(file)
            data = data['locations']
            total_distance = calculate_distance(data, start_date, end_date)
            around_the_earth = total_distance / 40775
            to_moon = total_distance / 384400
            total_distance = f'{round(total_distance, 2):,}'.replace(',', '\'')
            return render_template('index.html', total_distance=total_distance, around_the_earth=around_the_earth,
                                   to_moon=to_moon)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
