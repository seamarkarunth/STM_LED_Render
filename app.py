import os
import secrets
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

# Set this as an environment variable in Render.
CONTROL_TOKEN = os.environ.get("CONTROL_TOKEN", "")
led_state = False

PAGE = """
<!doctype html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>STM32 LED Control</title>
</head>
<body>
  <h1>STM32 LED Control</h1>
  <button onclick="setLed(true)">LED ON</button>
  <button onclick="setLed(false)">LED OFF</button>
  <p id="status">Loading...</p>
  <script>
    async function updateStatus() {
      const r = await fetch('/api/state');
      const d = await r.json();
      document.getElementById('status').textContent =
        'LED is ' + (d.led ? 'ON' : 'OFF');
    }
    async function setLed(on) {
      const token = prompt('Enter the control token:');
      if (!token) return;
      await fetch('/api/state', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Control-Token': token
        },
        body: JSON.stringify({led: on})
      });
      updateStatus();
    }
    updateStatus();
    setInterval(updateStatus, 3000);
  </script>
</body>
</html>
"""

@app.get("/")
def home():
    return render_template_string(PAGE)

@app.get("/api/state")
def get_state():
    return jsonify({"led": led_state})

@app.post("/api/state")
def set_state():
    global led_state

    if not CONTROL_TOKEN:
        return jsonify({"error": "Server token is not configured"}), 503

    supplied = request.headers.get("X-Control-Token", "")
    if not secrets.compare_digest(supplied, CONTROL_TOKEN):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    if not isinstance(data.get("led"), bool):
        return jsonify({"error": "Send led as true or false"}), 400

    led_state = data["led"]
    return jsonify({"led": led_state})
