#include "gps_parser.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Hàm bổ trợ: Trích xuất chuỗi con nằm giữa hai vị trí con trỏ
static void extract_field(const char *start, const char *end, char *buffer) {
  int len = end - start;
  memcpy(buffer, start, len);
  buffer[len] = '\0'; // Kết thúc chuỗi an toàn
}

void parse_nmea_gprmc(const char *nmea_str, GPSPacket_t *packet) {
  // Kiểm tra xem có đúng là chuỗi GPRMC không
  if (strstr(nmea_str, "$GPRMC") == NULL)
    return;

  char token[32];
  const char *current = nmea_str;
  const char *next = NULL;
  int field_index = 0;

  // Vòng lặp quét qua chuỗi bằng con trỏ để nhặt từng trường dữ liệu qua dấu
  // phẩy
  while ((next = strchr(current, ',')) != NULL || field_index == 11) {
    // Nếu không tìm thấy dấu phẩy tiếp theo (trường cuối cùng), cho 'next' trỏ
    // tới cuối chuỗi
    if (next == NULL) {
      next = current + strlen(current);
    }

    // Trích xuất chuỗi con nằm giữa biến 'current' và biến 'next'
    extract_field(current, next, token);

    // Phân tích dữ liệu dựa vào số thứ tự của dấu phẩy (Field Index)
    if (strlen(token) > 0) {
      switch (field_index) {
      case 1: { // Trường số 1: Thời gian UTC (Ví dụ: "123519")
        long raw_time = atol(token);
        packet->hour = (uint8_t)(raw_time / 10000);
        packet->minute = (uint8_t)((raw_time % 10000) / 100);
        packet->second = (uint8_t)(raw_time % 100);
        break;
      }
      case 3: { // Trường số 3: Vĩ độ dạng DDMM.MMMM (Ví dụ: "4807.038")
        float raw_lat = atof(token);
        int degrees = (int)(raw_lat / 100);
        float minutes = raw_lat - (degrees * 100);
        packet->latitude =
            degrees +
            (minutes / 60.0f); // Đổi sang Độ thập phân (Decimal Degrees)
        break;
      }
      case 4: { // Trường số 4: Hướng Vĩ độ 'N' hoặc 'S'
        if (token[0] == 'S')
          packet->latitude = -packet->latitude;
        break;
      }
      case 5: { // Trường số 5: Kinh độ dạng DDDMM.MMMM (Ví dụ: "01131.000")
        float raw_lon = atof(token);
        int degrees = (int)(raw_lon / 100);
        float minutes = raw_lon - (degrees * 100);
        packet->longitude =
            degrees + (minutes / 60.0f); // Đổi sang Độ thập phân
        break;
      }
      case 6: { // Trường số 6: Hướng Kinh độ 'E' hoặc 'W'
        if (token[0] == 'W')
          packet->longitude = -packet->longitude;
        break;
      }
      case 7: { // Trường số 7: Vận tốc di chuyển (Tốc độ tính bằng Knots: Hải
                // lý/giờ)
        packet->speed_kmph = atof(
            token); // Tạm thời lưu theo Knots, Python có thể đổi sang km/h sau
        break;
      }
      default:
        break; // Các trường khác không xử lý
      }
    }
    // Nhảy tới ký tự tiếp theo sau dấu phẩy để bắt đầu vòng lặp mới
    if (next == NULL)
      break;
    current = next + 1;
    field_index++;
  }
}

// Hàm chuyển đổi Struct thô sang chuỗi Hex (Ví dụ: "AA0050005F0A")
void serialize_gps_packet(const GPSPacket_t *packet, char *output_hex) {
  uint8_t *raw_ptr = (uint8_t *)packet;
  for (size_t i = 0; i < sizeof(GPSPacket_t); i++) {
    // In từng byte dưới dạng Hex 2 ký tự (in hoa) vào chuỗi
    sprintf(output_hex + (i * 2), "%02X", raw_ptr[i]);
  }
}