import paho.mqtt.client as mqtt
from datetime import datetime
import time
import json  # Import thư viện json

BROKER = "192.168.0.100"  # Địa chỉ IP của MQTT Broker
PORT = 1883
TOPIC = "MQTT_DongCo_DCs2"    # Tên topic

# Hàm kết nối
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Kết nối MQTT Broker thành công!")
    else:
        print(f"Kết nối thất bại. Lỗi mã: {rc}")

# Tạo client MQTT
client = mqtt.Client()
client.on_connect = on_connect

# Kết nối tới broker
client.connect(BROKER, PORT, 60)

client.loop_start()  # Khởi động vòng lặp xử lý
try:
    while True:
        # Tạo dữ liệu JSON
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")  # Lấy ngày hiện tại
        current_time = now.strftime("%H:%M:%S")  # Lấy giờ hiện tại
        data = {
            "date": current_date,        # Ngày
            "time": current_time,        # Giờ
            "ThanhVien1": "Trung Dung",    # Thông tin thêm
            "ThanhVien2": "Phuong Nam"
        }

        # Gửi dữ liệu dạng JSON
        client.publish(TOPIC, json.dumps(data))
        print(f"Đã gửi: {json.dumps(data)}")
        time.sleep(1)  # Gửi mỗi 5 giây
except KeyboardInterrupt:
    print("Dừng chương trình.")
    client.loop_stop()