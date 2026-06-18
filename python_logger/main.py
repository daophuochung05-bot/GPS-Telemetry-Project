import csv
import os
import sys
from decoder import decode_hex_gps

def main():
    print("--- GPS DIAGNOSTIC & LOGGER TOOL RUNNING ---")
    print("Đang lắng nghe dữ liệu hành trình thời gian thực từ hộp ECU C...")
    print("Nhấn Ctrl + C để dừng hệ thống và xuất bản đồ.\n")

    # 1. THIẾT LẬP ĐƯỜNG DẪN TUYỆT ĐỐI AN TOÀN
    # Tự động tìm vị trí thư mục hiện tại của file main.py để định vị chính xác vị trí lưu dữ liệu
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_dir = os.path.join(project_root, "data")
    
    # Tạo thư mục 'data/' nếu hệ thống chưa có sẵn
    os.makedirs(data_dir, exist_ok=True)
    csv_file = os.path.join(data_dir, "gps_route.csv")
    map_file = os.path.join(data_dir, "vehicle_map.html")

    # Tiêu đề các cột dữ liệu hành trình để lưu file CSV
    headers = ["Time_UTC", "Latitude", "Longitude", "Speed_Knots", "Speed_KmH"]
    
    # Kiểm tra xem file log đã có chưa, nếu chưa thì tạo mới và viết dòng tiêu đề (Header)
    file_exists = os.path.exists(csv_file)
    with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)

    # Mảng lưu danh sách các tọa độ điểm xe chạy qua để chuẩn bị vẽ đường vạch hành trình
    coordinate_history = []

    try:
        # 2. VÒNG LẶP HỨNG LUỒNG DỮ LIỆU TỪ PIPE SYSTEM (sys.stdin)
        for line in sys.stdin:
            # Loại bỏ ký tự xuống dòng rác (\n) ở cuối chuỗi Hex
            hex_data = line.strip()
            if not hex_data:
                continue

            # Tiến hành chuyển sang trạm giải mã dữ liệu nhị phân
            gps_info = decode_hex_gps(hex_data)

            # Nếu dữ liệu chuẩn (không phải chữ tiêu đề rác hoặc lỗi lề)
            if gps_info is not None:
                # In trực quan kết quả chẩn đoán ra màn hình Terminal
                print(f"[GPS DATA] Thời gian: {gps_info['time']} | "
                      f"Vĩ độ: {gps_info['latitude']} | Kinh độ: {gps_info['longitude']} | "
                      f"Vận tốc: {gps_info['speed_kmh']} km/h")

                # Lưu trữ tọa độ vào mảng lịch sử để phục vụ vẽ bản đồ hành trình
                coordinate_history.append((gps_info['latitude'], gps_info['longitude']))

                # GHI CUỐN CHIẾU THỜI GIAN THỰC VÀO FILE CSV
                with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        gps_info['time'],
                        gps_info['latitude'],
                        gps_info['longitude'],
                        gps_info['speed_knots'],
                        gps_info['speed_kmh']
                    ])
                    # LỆNH ÉP BUỘC: Xả bộ đệm ổ cứng ngay tức khắc để bảo toàn dữ liệu kể cả khi tắt đột ngột
                    f.flush()

    except KeyboardInterrupt:
        print("\n[INFO] Đã nhận tín hiệu ngắt Ctrl + C từ người dùng.")
    
    finally:
        # 3. TRỰC QUAN HÓA HÀNH TRÌNH LÊN BẢN ĐỒ VỆ TINH (ỨNG DỤNG NÂNG CAO)
        if coordinate_history:
            print("Đang tiến hành dựng đường vẽ di chuyển của xe thông minh...")
            try:

                import folium # Thư viện vẽ bản đồ tương tác siêu nhẹ
                
                # Lấy điểm tọa độ đầu tiên làm tâm điểm mở bản đồ
                start_lat, start_lon = coordinate_history[0]
                my_map = folium.Map(location=[start_lat, start_lon], zoom_start=16)

                # Vẽ một đường vạch màu đỏ (PolyLine) nối liền toàn bộ các điểm tọa độ mà xe đã đi qua
                folium.PolyLine(coordinate_history, color="red", weight=4, opacity=0.8).add_to(my_map)

                # Đánh dấu điểm bắt đầu hành trình (Màu xanh lá) và điểm kết thúc hành trình (Màu đỏ)
                folium.Marker(coordinate_history[0], popup="Start Route", icon=folium.Icon(color='green')).add_to(my_map)
                folium.Marker(coordinate_history[-1], popup="End Route", icon=folium.Icon(color='red')).add_to(my_map)

                # Lưu bản đồ ra thành một file web .html
                my_map.save(map_file)
                print(f"➔ [THÀNH CÔNG] Đã xuất file bản đồ hành trình tại: {map_file}")
                print("Mẹo: Em chỉ cần double-click mở file .html này bằng trình duyệt Chrome/Edge để xem xe chạy nhé!")
            except ImportError:
                print("➔ [GỢI Ý] Để vẽ được bản đồ hành trình, em hãy gõ lệnh 'pip install folium' vào Terminal nhé.")
        
        print("Hệ thống giám sát định vị đóng cửa an toàn. Tạm biệt em!")

if __name__ == "__main__":
    main()