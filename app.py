from flask import Flask, request

app = Flask(__name__)

# Global variables to store the latest sensor readings
# (In a real app, you'd use a database, but this works for now!)
sensor_data = {
    "pressure": 0,
    "temperature": 0
}

@app.route('/')
def home():
    # This is what you see when you visit your website
    return f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="2"> <style>
                body {{ font-family: sans-serif; text-align: center; padding: 50px; }}
                .box {{ border: 2px solid #333; padding: 20px; display: inline-block; margin: 10px; }}
            </style>
        </head>
        <body>
            <h1>My Hand Sensor Data</h1>
            <div class="box">
                <h2>Pressure</h2>
                <p style="font-size: 40px; color: blue;">{sensor_data['pressure']}</p>
            </div>
            <div class="box">
                <h2>Temperature</h2>
                <p style="font-size: 40px; color: red;">{sensor_data['temperature']}</p>
            </div>
        </body>
    </html>
    """

@app.route('/update', methods=['POST'])
def update_data():
    # This is the secret door your computer uses to upload data
    global sensor_data
    try:
        data = request.json
        sensor_data['pressure'] = data.get('pressure', 0)
        sensor_data['temperature'] = data.get('temperature', 0)
        return "Data Received!", 200
    except Exception as e:
        return f"Error: {e}", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
