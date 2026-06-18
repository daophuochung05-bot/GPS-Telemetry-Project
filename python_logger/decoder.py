import struct
import re

def decode_hex_gps(hex_string):
    """
    Hàm giải mã chuỗi Hex nhận được từ chương trình C thành dữ liệu số học thực tế.
    """
    try:
        # 1. DỌN RÁC: Chỉ giữ lại các ký tự hợp lệ của hệ thập lục phân (0-9, a-f, A-F)
        clean_hex = "".join(re.findall(r'[0-9a-fA-F]', hex_string))
        
        # 2. KIỂM TRA ĐỘ DÀI: Struct C (GPSPacket_t) nặng đúng 15 bytes nhị phân
        # 15 bytes * 2 ký tự Hex = 30 ký tự chữ. Sai độ dài lập tức loại bỏ
        if len(clean_hex) != 30:
            return None
            
        # 3. CHUYỂN ĐỔI: Biến chuỗi chữ 30 ký tự Hex thành mảng 15 bytes thô trong RAM
        raw_bytes = bytes.fromhex(clean_hex)
        
        # 4. GIẢI MÃ (UNPACK): Sử dụng dao cắt bộ nhớ theo đúng bản thiết kế từ C
        # Định dạng '<BBBfff' nghĩa là:
        #   < : Định dạng đọc Little-endian (chuẩn của chip Intel/AMD/ARM)
        #   BBB : 3 biến Unsigned Char (1 byte mỗi biến) dành cho Giờ, Phút, Giây
        #   fff : 3 biến Float (4 bytes mỗi biến) dành cho Vĩ độ, Kinh độ, Tốc độ
        # Tổng cộng: 1 + 1 + 1 + 4 + 4 + 4 = 15 bytes khít khao!
        hour, minute, second, latitude, longitude, speed = struct.unpack('<BBBfff', raw_bytes)
        
        # Đóng gói dữ liệu sạch vào một cuốn từ điển (Dictionary) để xuất xưởng
        return {
            "time": f"{hour:02d}:{minute:02d}:{second:02d}",
            "latitude": round(latitude, 5),
            "longitude": round(longitude, 5),
            "speed_knots": round(speed, 2),
            "speed_kmh": round(speed * 1.852, 2) # Đổi từ Hải lý/giờ sang km/h thực tế của ô tô
        }
        
    except Exception:
        # Nếu có bất kỳ sự cố méo mó dữ liệu nào trên đường truyền, âm thầm bỏ qua để hệ thống không bị crash
        return None