from argparse import ArgumentParser
from flask import Flask, render_template, Response, request
from os import listdir, O_NONBLOCK
from os.path import isfile, join
import csv
import json
import plotly.graph_objs as go
import plotly.io as pio
from plotly.subplots import make_subplots
import pandas as pd
import threading
import time
from enum import Enum
import datetime

csv_path = 'csv/'
packetdump_graph_update_time = 1  # in seconds
userstate_graph_update_time = 0.2  # in seconds

app = Flask(__name__)
app.secret_key = "asldkfjeori;ngkagieoirgiejgk;lsdgjsoreijw;ralgdkdfilj93852980571qioejfsofgiw984t3qpj;aslkdf"


class FlaskApp(threading.Thread):
    def __init__(self, target_file, userstate_file, target_ip, file_timestamp):
        threading.Thread.__init__(self)
        self.restore_flag = threading.Event()

        self.target_file = target_file
        self.userstate_file = userstate_file
        self.target_ip = target_ip
        self.file_timestamp = file_timestamp

    def run(self):
        """
        Entrypoint that gets started when the thread is invoked
        """
        run_flask(self.target_file, self.userstate_file, self.target_ip, self.file_timestamp)


def append_to_map(incoming_map, outgoing_map, incoming, outgoing):
    incoming_map.append(incoming)
    outgoing_map.append(outgoing)


def create_basic_plot():
    time_stamps = []  # timestamp in formatted string
    time_stamps_raw = []  # timestamp in Unix Epoch in seconds
    incoming_bytes = []
    outgoing_bytes = []
    udp_outgoing = []
    udp_incoming = []
    tcp_outgoing = []
    tcp_incoming = []
    other_connection_incoming = []
    other_connection_outgoing = []
    http_incoming = []
    http_outgoing = []
    https_incoming = []
    https_outgoing = []
    user_speaking = []

    with open(app.config['file'], 'r') as csv_data_file:
        print("Reading in csv file")
        csv_reader = csv.reader(csv_data_file)
        for row in csv_reader:
            x_val = time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(int(row[0])))
            incoming = int(row[1])
            outgoing = int(row[2])

            if x_val not in time_stamps:
                time_stamps.append(x_val)
                time_stamps_raw.append(int(row[0]))
                append_to_map(incoming_map=incoming_bytes,
                              outgoing_map=outgoing_bytes, incoming=incoming, outgoing=outgoing)

                if row[5] == "HTTP":
                    append_to_map(incoming_map=http_incoming, outgoing_map=http_outgoing,
                                  incoming=incoming, outgoing=outgoing)
                else:
                    append_to_map(incoming_map=http_incoming, outgoing_map=http_outgoing,
                                  incoming=0, outgoing=0)
                if row[5] == "HTTPS":
                    append_to_map(incoming_map=https_incoming, outgoing_map=https_outgoing,
                                  incoming=incoming, outgoing=outgoing)
                else:
                    append_to_map(incoming_map=https_incoming, outgoing_map=https_outgoing,
                                  incoming=0, outgoing=0)

                if row[6] == "UDP":
                    append_to_map(incoming_map=udp_incoming, outgoing_map=udp_outgoing,
                                  incoming=incoming, outgoing=outgoing)
                else:
                    append_to_map(incoming_map=udp_incoming, outgoing_map=udp_outgoing,
                                  incoming=0, outgoing=0)
                if row[6] == "TCP":
                    append_to_map(incoming_map=tcp_incoming, outgoing_map=tcp_outgoing,
                                  incoming=incoming, outgoing=outgoing)
                else:
                    append_to_map(incoming_map=tcp_incoming, outgoing_map=tcp_outgoing,
                                  incoming=0, outgoing=0)
                if row[6] == "None":
                    append_to_map(incoming_map=other_connection_incoming, outgoing_map=other_connection_outgoing,
                                  incoming=incoming, outgoing=outgoing)
                else:
                    append_to_map(incoming_map=other_connection_incoming, outgoing_map=other_connection_outgoing,
                                  incoming=0, outgoing=0)
            else:
                incoming_bytes[time_stamps.index(x_val)] += incoming
                outgoing_bytes[time_stamps.index(x_val)] += outgoing

                if row[5] == "HTTP":
                    http_incoming[time_stamps.index(x_val)] += incoming
                    http_outgoing[time_stamps.index(x_val)] += outgoing
                elif row[5] == "HTTPS":
                    https_incoming[time_stamps.index(x_val)] += incoming
                    https_outgoing[time_stamps.index(x_val)] += outgoing

                if row[6] == "UDP":
                    udp_incoming[time_stamps.index(x_val)] += incoming
                    udp_outgoing[time_stamps.index(x_val)] += outgoing
                elif row[6] == "TCP":
                    tcp_incoming[time_stamps.index(x_val)] += incoming
                    tcp_outgoing[time_stamps.index(x_val)] += outgoing
                elif row[6] == "None":
                    other_connection_incoming[time_stamps.index(
                        x_val)] += incoming
                    other_connection_outgoing[time_stamps.index(
                        x_val)] += outgoing

        # add data for graph "Is the User Talking to the Voice Assistant?"
        if app.config['userstate_file'] is not None:
            print("Reading in UserState csv file")
            userstate_data_file = open(app.config['userstate_file'], 'r')
            csv_reader_userstate = csv.reader(userstate_data_file)
            userstate_data = [row for row in csv_reader_userstate]

            prev_user_speaking = 0
            userstate_index = 0
            for timestamp in time_stamps_raw:
                if userstate_index >= len(userstate_data):
                    user_speaking.append(int(userstate_data[-1][1]))
                    continue
                if timestamp >= int(userstate_data[userstate_index][0]):
                    prev_user_speaking = int(userstate_data[userstate_index][1])
                    userstate_index += 1
                user_speaking.append(prev_user_speaking)

        # filter user_speaking datapoints that have value equals 1 only for better visual effects
        time_stamps_user_speaking = []
        user_speaking_graph = []
        for index, timestamp in enumerate(time_stamps):
            if index < len(user_speaking) and user_speaking[index] > 0:
                time_stamps_user_speaking.append(timestamp)
                user_speaking_graph.append(user_speaking[index])

    print("Done reading in csv file")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.update_yaxes(tickvals=[0, 1], title_text="Is the User Talking to the Device?", secondary_y=True)

    print("Adding traces to the figures ...")
    fig.add_trace(go.Scatter(
        x=time_stamps,
        y=incoming_bytes,
        mode='lines+markers',
        name='Overall Incoming',
    ))
    fig.add_trace(go.Scatter(
        x=time_stamps,
        y=outgoing_bytes,
        mode='lines+markers',
        name='Overall Outgoing'
    ))
    fig.add_trace(go.Scatter(
        x=time_stamps,
        y=udp_incoming,
        mode='lines+markers',
        name='UDP Incoming',
        visible="legendonly"
    ))
    fig.add_trace(go.Scatter(
        x=time_stamps,
        y=udp_outgoing,
        mode='lines+markers',
        name='UDP Outgoing',
        visible="legendonly"
    ))
    fig.add_trace(go.Scatter(
        x=time_stamps,
        y=tcp_incoming,
        mode='lines+markers',
        name='TCP Incoming',
        visible="legendonly"
    ))
    fig.add_trace(go.Scatter(
        x=time_stamps,
        y=tcp_outgoing,
        mode='lines+markers',
        name='TCP Outgoing',
        visible="legendonly"
    ))
    fig.add_trace(go.Scatter(
        x=time_stamps,
        y=other_connection_incoming,
        mode='lines+markers',
        name='Other Connection Protocol Incoming',
        visible="legendonly"
    ))
    fig.add_trace(go.Scatter(
        x=time_stamps,
        y=other_connection_outgoing,
        mode='lines+markers',
        name='Other Connection Protocol Outgoing',
        visible="legendonly"
    ))

    fig.add_trace(go.Scatter(
        x=time_stamps,
        y=http_incoming,
        mode='lines+markers',
        name='HTTP Incoming',
        visible="legendonly"
    ))
    fig.add_trace(go.Scatter(
        x=time_stamps,
        y=http_outgoing,
        mode='lines+markers',
        name='HTTP Outgoing',
        visible="legendonly"
    ))
    fig.add_trace(go.Scatter(
        x=time_stamps,
        y=https_incoming,
        mode='lines+markers',
        name='HTTPS Incoming',
        visible="legendonly"
    ))
    fig.add_trace(go.Scatter(
        x=time_stamps,
        y=https_outgoing,
        mode='lines+markers',
        name='HTTPS Outgoing',
        visible="legendonly"
    ))
    fig.add_trace(go.Scatter(
        x=time_stamps_user_speaking,
        y=user_speaking_graph,
        mode='markers',
        line=dict(color='gray', dash='dash'),
        marker=dict(color='gray', size=5),
        name="Is User Talking to the Device?",
        visible="legendonly",
    ), secondary_y=True)

    fig.update_layout(
        title="Bytes Sent over Time",
        xaxis_title="Time (s)",
        yaxis_title="Bytes",
        font=dict(
            family="Helvetica",
            size=18,
            color="#000000"
        )
    )

    print("Converting graph to JSON ...")
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
        class PacketDirection(Enum):
            Incoming = 0
            Outgoing = 1
            Unknown = 2

        def packetDirection(row):
            if row[7] == app.config['target']:  # srcip
                return PacketDirection.Outgoing
            elif row[8] == app.config['target']:  # dstip
                return PacketDirection.Incoming
            else:
                return PacketDirection.Unknown

        curr_time = -1
        cumulative_total_bytes = 0
        cumulative_incoming_bytes = 0
        cumulative_outgoing_bytes = 0
        cumulative_udp_incoming_bytes = 0
        cumulative_udp_outgoing_bytes = 0
        cumulative_tcp_incoming_bytes = 0
        cumulative_tcp_outgoing_bytes = 0
        cumulative_others_incoming_bytes = 0
        cumulative_others_outgoing_bytes = 0
        cumulative_http_incoming_bytes = 0
        cumulative_http_outgoing_bytes = 0
        cumulative_https_incoming_bytes = 0
        cumulative_https_outgoing_bytes = 0

        with open(csv_path + app.config['target_file'], 'r', O_NONBLOCK) as csv_data_file:
            while True:
                total_bytes = 0
                incoming_bytes = 0
                outgoing_bytes = 0
                udp_incoming_bytes = 0
                udp_outgoing_bytes = 0
                tcp_incoming_bytes = 0
                tcp_outgoing_bytes = 0
                others_incoming_bytes = 0
                others_outgoing_bytes = 0
                http_incoming_bytes = 0
                http_outgoing_bytes = 0
                https_incoming_bytes = 0
                https_outgoing_bytes = 0

                csv_reader = csv.reader(csv_data_file)
                for row in csv_reader:
                    if curr_time == -1:
                        curr_time = int(row[0])

                    curr_incoming_bytes = int(row[1])
                    curr_outgoing_bytes = int(row[2])
                    incoming_bytes += curr_incoming_bytes
                    outgoing_bytes += curr_outgoing_bytes
                    udp_incoming_bytes += curr_incoming_bytes if (
                        row[6] == 'UDP' and packetDirection(row) == PacketDirection.Incoming) else 0
                    udp_outgoing_bytes += curr_outgoing_bytes if (
                        row[6] == 'UDP' and packetDirection(row) == PacketDirection.Outgoing) else 0
                    tcp_incoming_bytes += curr_incoming_bytes if (
                        row[6] == 'TCP' and packetDirection(row) == PacketDirection.Incoming) else 0
                    tcp_outgoing_bytes += curr_outgoing_bytes if (
                        row[6] == 'TCP' and packetDirection(row) == PacketDirection.Outgoing) else 0
                    others_incoming_bytes += curr_incoming_bytes if (
                        row[6] != 'UDP' and row[6] != 'TCP' and packetDirection(row) == PacketDirection.Incoming) else 0
                    others_outgoing_bytes += curr_outgoing_bytes if (
                        row[6] != 'UDP' and row[6] != 'TCP' and packetDirection(row) == PacketDirection.Outgoing) else 0
                    http_incoming_bytes += curr_incoming_bytes if (
                        row[5] == 'HTTP' and packetDirection(row) == PacketDirection.Incoming) else 0
                    http_outgoing_bytes += curr_outgoing_bytes if (
                        row[5] == 'HTTP' and packetDirection(row) == PacketDirection.Outgoing) else 0
                    https_incoming_bytes += curr_incoming_bytes if (
                        row[5] == 'HTTPS' and packetDirection(row) == PacketDirection.Incoming) else 0
                    https_outgoing_bytes += curr_outgoing_bytes if (
                        row[5] == 'HTTPS' and packetDirection(row) == PacketDirection.Outgoing) else 0

                cumulative_total_bytes += incoming_bytes + outgoing_bytes
                cumulative_incoming_bytes += incoming_bytes
                cumulative_outgoing_bytes += outgoing_bytes
                cumulative_udp_incoming_bytes += udp_incoming_bytes
                cumulative_udp_outgoing_bytes += udp_outgoing_bytes
                cumulative_tcp_incoming_bytes += tcp_incoming_bytes
                cumulative_tcp_outgoing_bytes += tcp_outgoing_bytes
                cumulative_others_incoming_bytes += others_incoming_bytes
                cumulative_others_outgoing_bytes += others_outgoing_bytes
                cumulative_http_incoming_bytes += http_incoming_bytes
                cumulative_http_outgoing_bytes += http_outgoing_bytes
                cumulative_https_incoming_bytes += https_incoming_bytes
                cumulative_https_outgoing_bytes += https_outgoing_bytes

                curr_time += packetdump_graph_update_time
                if curr_time != -1:
                    total_bytes = incoming_bytes + outgoing_bytes
                    formatted_time = time.strftime(
                        '%Y-%m-%d %H:%M:%S', time.localtime(curr_time))
                    json_data = json.dumps({
                        'time': formatted_time,
                        'total_bytes': total_bytes,
                        'incoming_bytes': incoming_bytes,
                        'outgoing_bytes': outgoing_bytes,
                        'udp_incoming_bytes': udp_incoming_bytes,
                        'udp_outgoing_bytes': udp_outgoing_bytes,
                        'tcp_incoming_bytes': tcp_incoming_bytes,
                        'tcp_outgoing_bytes': tcp_outgoing_bytes,
                        'others_incoming_bytes': others_incoming_bytes,
                        'others_outgoing_bytes': others_outgoing_bytes,
                        'http_incoming_bytes': http_incoming_bytes,
                        'http_outgoing_bytes': http_outgoing_bytes,
                        'https_incoming_bytes': https_incoming_bytes,
                        'https_outgoing_bytes': https_outgoing_bytes,
                        'cumulative_total_bytes': cumulative_total_bytes,
                        'cumulative_incoming_bytes': cumulative_incoming_bytes,
                        'cumulative_outgoing_bytes': cumulative_outgoing_bytes,
                        'cumulative_udp_incoming_bytes': cumulative_udp_incoming_bytes,
                        'cumulative_udp_outgoing_bytes': cumulative_udp_outgoing_bytes,
                        'cumulative_tcp_incoming_bytes': cumulative_tcp_incoming_bytes,
                        'cumulative_tcp_outgoing_bytes': cumulative_tcp_outgoing_bytes,
                        'cumulative_others_incoming_bytes': cumulative_others_incoming_bytes,
                        'cumulative_others_outgoing_bytes': cumulative_others_outgoing_bytes,
                        'cumulative_http_incoming_bytes': cumulative_http_incoming_bytes,
                        'cumulative_http_outgoing_bytes': cumulative_http_outgoing_bytes,
                        'cumulative_https_incoming_bytes': cumulative_https_incoming_bytes,
                        'cumulative_https_outgoing_bytes': cumulative_https_outgoing_bytes
                    })
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
                        {'time': formatted_time, 'user_speaking': user_speaking}
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


def run_flask(file, userstate_file, target, stamp):
    if file:
        app.config['file'] = file
        app.config['userstate_file'] = userstate_file
        app.run(debug=False, threaded=True)
    else:
        if target and stamp:
            app.config['target'] = target
            app.config['timestamp'] = stamp
            app.config['target_file'] = get_latest_packetdump_csv(
                target, stamp)
            app.config['userstate_file'] = get_latest_userstate_csv(
                target, stamp)
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
            app.config['target_file'] = get_latest_packetdump_csv(
                args.target, args.stamp)
            app.config['userstate_file'] = get_latest_userstate_csv(
                args.target, args.stamp)
            app.run(debug=True, threaded=True)
        else:
            print("Flask server requires either -f argument or -t and -s arguments")
