from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit
import paho.mqtt.client as mqtt
import time
import json
from datetime import datetime
from threading import Thread

# Thiết lập MQTT
MQTT_BROKER = "192.168.0.100"  # Broker MQTT, có thể thay đổi theo nhu cầu của bạn
MQTT_PORT = 1883
MQTT_TOPIC = "MQTT_DongCo_DCs2"  # Chủ đề MQTT của bạn
client = mqtt.Client()

# Thiết lập Flask
app = Flask(__name__)
socketio = SocketIO(app)

# Biến toàn cục để lưu trữ dữ liệu
data = "Chưa có dữ liệu"

# Hàm nhận dữ liệu từ MQTT
def on_message(client, userdata, message):
    global data
    data = message.payload.decode("utf-8")  # Cập nhật dữ liệu từ
    socketio.emit('mqtt_data', data)  # Gửi dữ liệu qua WebSocket đến clien

# Hàm kết nối với MQTT
def connect_mqtt():
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.subscribe(MQTT_TOPIC)
    client.loop_start()

# Hàm gửi dữ liệu lên MQTT với thông tin date, time, và status
def send_mqtt_message(msg, motor_speed="0"):
    # Lấy thời gian hiện tại
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Tạo chuỗi JSON
    data_to_send = {
        "date": current_time.split(" ")[0],  # Lấy ngày (YYYY-MM-DD)
        "time": current_time.split(" ")[1],  # Lấy giờ (HH:MM:SS)
        "status": msg,  # Trạng thái động cơ
        "Tốc độ động cơ": motor_speed  # Tốc độ động cơ
    }
    # Chuyển đổi thành chuỗi JSON
    json_message = json.dumps(data_to_send)
    # Gửi chuỗi JSON qua MQTT
    client.publish(MQTT_TOPIC, json_message)

# Hàm điều khiển động cơ bật/tắt
def control_motor(action, speed):
    if action == "on":
        send_mqtt_message("Motor is ON", motor_speed=speed)  # Gửi lệnh bật động cơ kèm tốc độ
    elif action == "off":
        send_mqtt_message("Motor is OFF", motor_speed="0")  # Gửi lệnh tắt động cơ

# Đoạn mã Flask để phục vụ giao diện người dùng
@app.route("/", methods=["GET", "POST"])
def index():
    global data
    if request.method == "POST":
        user_input = request.form["input_data"]
        motor_action = request.form.get("motor_action")
        motor_speed = request.form.get("motor_speed")  # Lấy tốc độ động cơ từ người dùng

        if motor_action:  # Kiểm tra nếu người dùng chọn điều khiển động cơ
            control_motor(motor_action, motor_speed)

        send_mqtt_message(user_input)  # Gửi dữ liệu nhập từ người dùng lên MQTT
        return render_template_string(template, time_display=time.strftime("%Y-%m-%d %H:%M:%S"), data=data, input_data=user_input)
    return render_template_string(template, time_display=time.strftime("%Y-%m-%d %H:%M:%S"), data=data, input_data="")

# Giao diện HTML
template = '''
<!DOCTYPE html>
<html>
<head>
    <title>MQTT Web Interface</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.0/socket.io.min.js"></script>
    <script type="text/javascript">
        var socket = io.connect('http://' + document.domain + ':' + location.port);
        socket.on('mqtt_data', function(data) {
            document.getElementById("mqtt_data").innerText = data;
        });
    </script>
</head>
<body>
    <div class="container">
        <h2>MQTT Web Interface</h2>
        <p><strong>Thời gian hiện tại:</strong> {{ time_display }}</p>
        <p><strong>Dữ liệu nhận được từ MQTT:</strong>{{ data }}</p>
    
        <form method="POST">
            <label for="input_data">Nhập thông tin:</label>
            <input type="text" id="input_data" name="input_data" value="{{ input_data }}" required>
            <button type="submit">Gửi dữ liệu</button>
        </form>
    </div>
</body>
</html>
'''

if __name__ == "__main__":
    # Kết nối MQTT trong một thread riêng biệt
    mqtt_thread = Thread(target=connect_mqtt)
    mqtt_thread.start()

    # Chạy ứng dụng Flask
    app.run(debug=True, host="0.0.0.0", port=5000)
