from flask import Flask, jsonify
import requests
import time
import threading

app = Flask(__name__)

# Machine URLs
machine_urls = {
    "Filling": "https://inpossystem-default-rtdb.firebaseio.com/ENERGY_F.json",
    "Sealing": "https://inpossystem-default-rtdb.firebaseio.com/ENERGY_S.json",
    "Labelling": "https://inpossystem-default-rtdb.firebaseio.com/ENERGY_L.json",
    "Rinding": "https://inpossystem-default-rtdb.firebaseio.com/ENERGY_E.json",
}

# Store last 3 voltages per machine
voltage_histories = {name: [] for name in machine_urls}
machine_statuses = {name: "Collecting" for name in machine_urls}

def fetch_voltage(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            value_str = str(data.get('value') if isinstance(data, dict) else data)
            return value_str[2:7] if len(value_str) >= 7 else None
    except:
        return None

def monitor_machines():
    while True:
        for machine_name, url in machine_urls.items():
            voltage = fetch_voltage(url)

            if voltage:
                voltage_histories[machine_name].append(voltage)
                if len(voltage_histories[machine_name]) > 3:
                    voltage_histories[machine_name].pop(0)

                if len(voltage_histories[machine_name]) == 3:
                    if all(v == voltage_histories[machine_name][0] for v in voltage_histories[machine_name]):
                        machine_statuses[machine_name] = "OFF"
                    else:
                        machine_statuses[machine_name] = "ON"
            #     else:
            #         machine_statuses[machine_name] = "Collecting"
            # else:
            #     machine_statuses[machine_name] = "Unavailable"

        time.sleep(1)

# Run monitoring in the background
threading.Thread(target=monitor_machines, daemon=True).start()

@app.route("/status", methods=["GET"])
def get_machine_status():
    return jsonify(machine_statuses)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
