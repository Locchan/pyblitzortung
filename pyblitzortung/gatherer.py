#!/usr/bin/env python3

import websocket
import random
import json
import pymysql.cursors
import datetime
import argparse
import os

VERSION = "1.1.1"

print(f"Started pyblitzortung version {VERSION}")

parser = argparse.ArgumentParser(prog='pyblitzortung', description='Blitzortung parser with output to a simple SQLite database')
parser.add_argument('-d', '--database-path', help="Path to create/write to", required=False, default="strikes.sqlite")
parser.add_argument('-m', '--metrics-path', help="Path to output metrics to (Prometheus-style metrics)", required=False, default="pyblitzortung.metrics")
args = parser.parse_args()

DATABASE_PATH = args.database_path
MONITORING_PATH = args.metrics_path

counter = 0
mon_metrics = {
    "strikes_total": 0,
    "errors": 0,
    "reconnects": -1
}

def init_database():
    db = pymysql.connect(
        host=os.environ['MYSQL_HOST'],
        user=os.environ['MYSQL_USERNAME'],
        password=os.environ['MYSQL_PASSWORD'],
        database=os.environ["MYSQL_DATABASE"],
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS strikes (id UNSIGNED BIGINT NOT NULL AUTO_INCREMENT, time UNSIGNED BIGINT, lat FLOAT, lon FLOAT, PRIMARY KEY (id));")
    return db, cursor

def deobf_message(ciphertext: str) -> str:
    chars = iter(ciphertext)

    c = next(chars, None)
    if c is None:
        return ""
    
    prev = c
    out = c
    dict = []

    for char in chars:
        code = ord(char)

        a = char if code < 256 else dict[code - 256] if code - 256 < len(dict) else f"{prev}{c}"
        out += a
        c = a[0]
        dict.append(f"{prev}{c}")
        prev = a

    return out
    
def gen_random_url():
    known_wss = ["ws1", "ws7", "ws8"]
    return f"wss://{random.choice(known_wss)}.blitzortung.org/"

def export_monitoring_metrics():
    with open(MONITORING_PATH, "w") as mon_file:
        for akey, aval in mon_metrics.items():
            mon_file.write(f"pyblitzortung_{akey} {aval}\n")

def on_message(ws, message):
    global counter
    message = deobf_message(message)
    message_dict = json.loads(message)
    
    db.ping(reconnect=True)
    sql = "INSERT INTO strikes (time, lat, lon) VALUES (%s, %s, %s);"
    cursor.execute(sql, [message_dict["time"], message_dict["lat"], message_dict["lon"]])
    
    counter += 1
    if counter == 100:
        counter = 0
        mon_metrics["strikes_total"] += 100
        print(f"{datetime.datetime.now()}: Committed 100 strikes.")
        db.commit()
        export_monitoring_metrics()
    #print(f"Added a strike at lat: {strike[1]} lon: {strike[2]}")

def on_error(ws, error):
    print(f"Encountered error: {error}")
    mon_metrics["errors"] += 1
    connect()

def on_close(ws, close_status_code, close_msg):
    print(f"Connection closed: {close_status_code}: {close_msg}")
    connect()

def on_open(ws):
    print("Connection opened")
    ws.send('{"a": 111}')

def connect():
    mon_metrics["reconnects"] += 1
    url = gen_random_url()
    print(f"Connecting to '{url}'...")
    ws = websocket.WebSocketApp(url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()


db, cursor = init_database()
connect()