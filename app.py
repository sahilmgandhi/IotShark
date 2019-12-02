from argparse import ArgumentParser
from flask import Flask, render_template, Response, request
from os import listdir, O_NONBLOCK
from os.path import isfile, join
import csv
import json
import plotly.graph_objs as go
import plotly.io as pio
import pandas as pd
import threading
import time
csv_path = 'csv/'
packetdump_graph_update_time = 1  # in seconds
userstate_graph_update_time = 0.2  # in seconds

app = Flask(__name__)
app.secret_key = "asldkfjeori;ngkagieoirgiejgk;lsdgjsoreijw;ralgdkdfilj93852980571qioejfsofgiw984t3qpj;aslkdf"


class FlaskApp(threading.Thread):
    def __init__(self, target_file, target_ip, file_timestamp):
        threading.Thread.__init__(self)
        self.restore_flag = threading.Event()

        self.target_file = target_file
        self.target_ip = target_ip
        self.file_timestamp = file_timestamp

    def run(self):
        """
        Entrypoint that gets started when the thread is invoked
        """
        run_flask(self.target_file, self.target_ip, self.file_timestamp)


def create_basic_plot():
    time_stamps = []
    incoming_bytes = []
    outgoing_bytes = []

    start_time = -1
    with open(app.config['file'], 'r') as csv_data_file:
        print("Reading in csv file")
        csv_reader = csv.reader(csv_data_file)
        for row in csv_reader:
            if start_time == -1:
                start_time = int(row[0])
            x_val = int(row[0]) - start_time
            if x_val not in time_stamps:
                time_stamps.append(x_val)
                incoming_bytes.append(int(row[1]))
                outgoing_bytes.append(int(row[2]))
            else:
                incoming_bytes[time_stamps.index(x_val)] += int(row[1])
                outgoing_bytes[time_stamps.index(x_val)] += int(row[2])

    print("Done reading in csv file")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=time_stamps,  # assign x as the dataframe column 'x'
        y=incoming_bytes,
        mode='lines+markers',
        name='Incoming Bytes'
    ))
    fig.add_trace(go.Scatter(
        x=time_stamps,  # assign x as the dataframe column 'x'
        y=outgoing_bytes,
        mode='lines+markers',
        name='Outgoing Bytes'
    ))

    fig.update_layout(
        title="Bytes Sent over Time",
        xaxis_title="Time in Seconds",
        yaxis_title="Number of Bytes",
        font=dict(
            family="Helvetica",
            size=18,
            color="#000000"
        )
    )

    print("Converting graph to JSON")
    graphJSON = pio.to_json(fig)
    print("Finished converting graph to JSON")
    return graphJSON


def get_latest_packetdump_csv(target, timestamp):
    file_name = 'packetdump_' + target + '_' + timestamp + '.csv'
    # wait until PySharkCapture creates file
    while file_name not in listdir(csv_path):
        pass
    return file_name

def get_latest_userstate_csv(target, timestamp):
    return 'userstate_' + target + '_' + timestamp + '.csv'

@app.route('/chart-data')
def chart_data():
    def parse_csv():
        curr_time = -1
        with open(csv_path + app.config['target_file'], 'r', O_NONBLOCK) as csv_data_file:
            while True:
                total_bytes = 0
                incoming_bytes = 0
                outgoing_bytes = 0
                no_new_data = True
                csv_reader = csv.reader(csv_data_file)
                for row in csv_reader:
                    if curr_time == -1:
                        curr_time = int(row[0])
                    incoming_bytes += int(row[1])
                    outgoing_bytes += int(row[2])
                    last_time = row[0]
                curr_time += packetdump_graph_update_time
                if curr_time != -1:
                    total_bytes = incoming_bytes + outgoing_bytes
                    formatted_time = time.strftime(
                        '%Y-%m-%d %H:%M:%S', time.localtime(curr_time))
                    json_data = json.dumps(
                        {'time': formatted_time, 'total_bytes': total_bytes, 'incoming_bytes': incoming_bytes, 'outgoing_bytes': outgoing_bytes})
                    yield f"data:{json_data}\n\n"
                time.sleep(packetdump_graph_update_time)

    return Response(parse_csv(), mimetype='text/event-stream')

@app.route('/user-state-data')
def user_state_data():
    # stream the User State data (Ex. the user starts/ends speaking to the voice assistant)
    def parse_csv():
        with open(csv_path + app.config['userstate_file'], 'r', O_NONBLOCK) as csv_data_file:
            while True:
                csv_reader = csv.reader(csv_data_file)
                for row in csv_reader:
                    curr_time = int(row[0])
                    user_speaking = int(row[1])
                    formatted_time = time.strftime(
                        '%Y-%m-%d %H:%M:%S', time.localtime(curr_time))
                    json_data = json.dumps(
                        { 'time': formatted_time, 'user_speaking': user_speaking }
                    )
                    yield f"data:{json_data}\n\n"
                    time.sleep(userstate_graph_update_time)
        
    return Response(parse_csv(), mimetype='text/event-stream')

@app.route("/")
def home():
    if 'file' in app.config:
        bytes_over_time_bar = create_basic_plot()
        json_file_name = app.config['file'][:-4] + '.json'
        with open(json_file_name) as json_file:
            data = json.load(json_file)

        return render_template('static_index.html', plot=bytes_over_time_bar, csv_file=app.config['file'], json_data=data, json_file=json_file_name)
    else:
        return render_template('dynamic_index.html')


def run_flask(file, target, stamp):
    if file:
        app.config['file'] = file
        app.run(debug=False, threaded=True)
    else:
        if target and stamp:
            app.config['target'] = target
            app.config['timestamp'] = stamp
            app.config['target_file'] = get_latest_packetdump_csv(target, stamp)
            app.config['userstate_file'] = get_latest_userstate_csv(target, stamp)
            app.run(debug=False, threaded=True)
        else:
            print(
                "Flask server requires either file argument or target and stamp arguments")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-t", "--target", dest="target",
                        help="Target IP")
    parser.add_argument("-f", "--file", dest="file",
                        help="CSV file containing captured data")
    parser.add_argument("-s", "--stamp", dest="stamp",
                        help="Timestamp of file containing csv data")
    args = parser.parse_args()

    if args.file:
        app.config['file'] = args.file
        app.run(debug=True, threaded=True)
    else:
        if args.target and args.stamp:
            app.config['target'] = args.target
            app.config['timestamp'] = args.stamp
            app.config['target_file'] = get_latest_packetdump_csv(args.target, args.stamp)
            app.config['userstate_file'] = get_latest_userstate_csv(args.target, args.stamp)
            app.run(debug=True, threaded=True)
        else:
            print("Flask server requires either -f argument or -t and -s arguments")
