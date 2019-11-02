import csv, math
from flask import Flask, request, jsonify, render_template
from datetime import time

app = Flask(__name__)

#Dictionary to fetch route id from trip id.
trips_file = csv.DictReader(open("data/trips.csv"))
trips = {}
for row in trips_file:
    trips[row["trip_id"]] = row["route_id"]

#Dictionary -> A list of arrival times and trip id for each stopId
stop_times_file = csv.DictReader(open("data/stop_times.csv"))
stop_times = {}
for row in stop_times_file:
    arr_time_arr = row["arrival_time"].split(':')
    if 23 > int(arr_time_arr[0]) > 0:
        arr_time = time(int(arr_time_arr[0]), int(arr_time_arr[1]), int(arr_time_arr[2]))
        if row["stop_id"] not in stop_times:
            stop_times[row["stop_id"]] = {}
        stop_times[row["stop_id"]].update({arr_time: row["trip_id"]})

#Sort the arrival times. Because we want the next three bus arrival times.
for stopId in stop_times:
    stop_times[stopId] = dict(sorted(stop_times[stopId].items()))

#Dictionary to store the latitude and longitude of each stop.
stops_file = csv.DictReader(open("data/stops.csv"))
stops = {}
for row in stops_file:
    stops[row["stop_id"]] = {'lat': float(row["stop_lat"]), 'lng': float(row["stop_lon"])}


#A function to calculate the distance between two sets of latitude and longitude
ang_rad = 0.1 / 6371
def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c
    return d

#API to get a list of stopIDs within 1km of user location
@app.route('/stopList', methods=['POST'])
def stopList():
    print(request.get_json())
    data = request.get_json()
    lat = data['pos']['lat']
    lng = data['pos']['lng']
    result = {}
    for stop in stops:
        lat2 = stops[stop]['lat']
        lng2 = stops[stop]['lng']
        dist_in_m = distance((lat, lng), (lat2, lng2))
        if dist_in_m <= 1:
            result[stop] = {'lat': lat2, 'lng': lng2}
    return jsonify(result), 200

#API to return next 3 buss times and routeId at a stopId
@app.route('/routesList', methods=['POST'])
def routesList():
    data = request.get_json()
    result = {}
    print(data['time'])
    time_arr=data['time'].split(':')
    reqested_stopId = data['stopId']
    requested_time = time(int(time_arr[0]), int(time_arr[1]), int(time_arr[2]))
    # requested_time = time(7, 41, 00) #demo request time.
    itr = 0
    for key, value in stop_times[reqested_stopId].items():
        if key > requested_time and itr < 3:
            result[str(key)] = trips[value]
            itr = itr + 1
        elif itr >= 3:
            break

    return jsonify(result), 200


@app.route('/')
def landing_page():
    return render_template('test.html')


if __name__ == '__main__':
    app.run()
