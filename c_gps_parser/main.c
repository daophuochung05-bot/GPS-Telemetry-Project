#include "gps_parser.h"
#include <stdio.h>
#include <unistd.h> // Thư viện chứa hàm sleep chuẩn Linux

int main() {
  // Giả lập một chuỗi danh sách hành trình di chuyển thực tế của xe thông minh
  const char *mock_nmea_database[] = {
      "$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A",
      "$GPRMC,123520,A,4807.045,N,01131.015,E,024.1,084.4,230394,003.1,W*6D",
      "$GPRMC,123521,A,4807.052,N,01131.030,E,025.8,084.4,230394,003.1,W*62",
      "$GPRMC,123522,A,4807.060,N,01131.042,E,026.5,084.4,230394,003.1,W*67",
      "$GPRMC,123523,A,4807.068,N,01131.058,E,028.2,084.4,230394,003.1,W*6F"};

  int total_sentences =
      sizeof(mock_nmea_database) / sizeof(mock_nmea_database[0]);
  int current_index = 0;

  // Vòng lặp vô hạn chạy liên tục thời gian thực (Real-time Blackbox
  // Simulation)
  while (1) {
    GPSPacket_t packet = {0}; // Khởi tạo gói tin trống sạch sẽ

    // Tạo một mảng ký tự chứa chuỗi Hex đầu ra. Size = (Kích thước struct * 2
    // ký tự) + 1 ký tự kết thúc chuỗi
    char hex_output[sizeof(GPSPacket_t) * 2 + 1] = {0};

    // Lấy chuỗi NMEA thô hiện tại từ cơ sở dữ liệu giả lập
    const char *current_nmea = mock_nmea_database[current_index];

    // 1. Kích hoạt trạm bóc tách dữ liệu chuỗi thô nạp vào Struct số học
    parse_nmea_gprmc(current_nmea, &packet);

    // 2. Kích hoạt trạm nén gói tin nhị phân trong struct thành chuỗi văn bản
    // Hex sạch
    serialize_gps_packet(&packet, hex_output);

    // 3. In duy nhất chuỗi Hex ra màn hình hệ thống kèm ký tự xuống dòng
    printf("%s\n", hex_output);

    // 4. LỆNH ÉP BUỘC: Xả kho đệm dữ liệu ngay lập tức để đẩy luồng qua Pipe
    // sang Python real-time
    fflush(stdout);

    // Chuyển sang tọa độ tiếp theo cho giây kế tiếp
    current_index = (current_index + 1) % total_sentences;

    // Tạm dừng 1 giây đúng chu kỳ lấy mẫu định vị
    sleep(1);
  }

  return 0;
}