import paho.mqtt.client as mqtt
import json  # Import thư viện json

BROKER = "192.168.0.103"
PORT = 1883
TOPIC = "Nhom9"

# Hàm callback khi kết nối thành công
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Kết nối MQTT Broker thành công!")
        client.subscribe(TOPIC)  # Đăng ký lắng nghe topic
    else:
        print(f"Kết nối thất bại. Lỗi mã: {rc}")

# Hàm callback khi nhận tin nhắn
def on_message(client, userdata, msg):
    try:
        # Giải mã chuỗi JSON
        data = json.loads(msg.payload.decode())
        print(f"Nhận từ {msg.topic}: {data}")
        print(f"Ngày: {data['date']}, Thời gian: {data['time']} , Thành Viên 1: {data['ThanhVien1']}, Thành Viên 2: {data['ThanhVien2']}")
    except json.JSONDecodeError:
        print("Không thể giải mã chuỗi JSON!")

# Tạo client MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Kết nối tới broker
client.connect(BROKER, PORT, 60)

# Chạy vòng lặp
client.loop_forever()