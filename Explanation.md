# Giải thích mã nguồn `gps_parser.c`

Tài liệu này giải thích chi tiết, dòng từng dòng cấu trúc và hoạt động của file [gps_parser.c](file:///run/media/hungdp/New%20Volume/Coding/gps_telemetry_project/c_gps_parser/gps_parser.c), chịu trách nhiệm phân tách gói tin định vị GPS chuẩn NMEA (GPRMC) và chuyển đổi struct dữ liệu sang dạng chuỗi Hexadecimal.

---

## 1. Khai báo thư viện (Dòng 1 - 4)

```c
#include "gps_parser.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
```

*   **`#include "gps_parser.h"`**: Nhúng file header [gps_parser.h](file:///run/media/hungdp/New%20Volume/Coding/gps_telemetry_project/c_gps_parser/gps_parser.h) để sử dụng định nghĩa struct [GPSPacket_t](file:///run/media/hungdp/New%20Volume/Coding/gps_telemetry_project/c_gps_parser/gps_parser.h#L10) và các nguyên mẫu hàm cần thiết.
*   **`#include <stdio.h>`**: Thư viện vào/ra chuẩn, được dùng để gọi hàm định dạng chuỗi `sprintf`.
*   **`#include <stdlib.h>`**: Thư viện tiện ích chuẩn, dùng để gọi hàm chuyển đổi chuỗi thành số:
    *   `atol` (Chuyển chuỗi thành số nguyên kiểu `long`).
    *   `atof` (Chuyển chuỗi thành số thực kiểu `float`).
*   **`#include <string.h>`**: Thư viện xử lý chuỗi, dùng để gọi các hàm:
    *   `memcpy` (Sao chép vùng nhớ).
    *   `strstr` (Tìm vị trí chuỗi con).
    *   `strchr` (Tìm vị trí ký tự đầu tiên xuất hiện).
    *   `strlen` (Đo độ dài chuỗi).

---

## 2. Hàm bổ trợ `extract_field` (Dòng 7 - 11)

Hàm này được dùng để trích xuất nội dung của một trường dữ liệu nằm giữa hai vị trí con trỏ `start` và `end`.

```c
static void extract_field(const char *start, const char *end, char *buffer) {
  int len = end - start;
  memcpy(buffer, start, len);
  buffer[len] = '\0'; // Kết thúc chuỗi an toàn
}
```

*   **`static`**: Giới hạn phạm vi của hàm chỉ nằm trong file `gps_parser.c` (hàm nội bộ), tránh xung đột tên với các file nguồn khác trong dự án.
*   **`int len = end - start;`**: Tính toán độ dài của trường dữ liệu bằng hiệu khoảng cách giữa hai con trỏ.
*   **`memcpy(buffer, start, len);`**: Sao chép `len` byte ký tự bắt đầu từ địa chỉ `start` vào vùng nhớ `buffer`.
*   **`buffer[len] = '\0';`**: Gán ký tự kết thúc chuỗi NULL (`\0`) vào cuối buffer để tạo thành một chuỗi C hợp lệ, ngăn chặn hiện tượng đọc tràn bộ nhớ.

---

## 3. Hàm phân tích gói tin `parse_nmea_gprmc` (Dòng 13 - 88)

Hàm thực hiện phân tích cú pháp chuỗi chuẩn GPS NMEA `$GPRMC` và gán dữ liệu vào struct.

### 3.1. Kiểm tra tính hợp lệ ban đầu
```c
  if (strstr(nmea_str, "$GPRMC") == NULL)
    return;
```
*   Sử dụng hàm `strstr` để kiểm tra chuỗi truyền vào có chứa từ khóa định danh `$GPRMC` hay không. Nếu không, hàm lập tức thoát (`return`).

### 3.2. Khai báo các biến con trỏ điều hướng
```c
  char token[32];
  const char *current = nmea_str;
  const char *next = NULL;
  int field_index = 0;
```
*   **`token[32]`**: Bộ đệm tạm thời chứa nội dung trường dữ liệu đang xét sau khi trích xuất.
*   **`current`**: Con trỏ trỏ tới điểm bắt đầu của trường hiện tại (ban đầu là đầu chuỗi).
*   **`next`**: Con trỏ trỏ tới vị trí của dấu phẩy tiếp theo.
*   **`field_index`**: Chỉ số thứ tự của trường dữ liệu cần bóc tách (phân cách bởi dấu phẩy).

### 3.3. Vòng lặp tách trường dữ liệu
```c
  while ((next = strchr(current, ',')) != NULL || field_index == 11) {
    if (next == NULL) {
      next = current + strlen(current);
    }
```
*   **`while (...)`**: Tìm kiếm ký tự dấu phẩy tiếp theo trong chuỗi bắt đầu từ vị trí `current`. Vòng lặp sẽ tiếp tục nếu tìm thấy dấu phẩy, hoặc khi đã đến trường dữ liệu cuối cùng (index 11).
*   **`if (next == NULL) ...`**: Nếu không còn dấu phẩy nào (trường cuối cùng), gán `next` bằng địa chỉ cuối cùng của chuỗi để bóc tách nốt phần dữ liệu còn lại.

```c
    extract_field(current, next, token);
```
*   Gọi hàm bổ trợ `extract_field` để sao chép trường dữ liệu nằm giữa con trỏ `current` và `next` vào mảng `token`.

### 3.4. Cấu trúc rẽ nhánh phân tích (Switch-case)
Nếu trường hiện tại có độ dài lớn hơn 0 (không bị rỗng), tiến hành phân tích dựa trên thứ tự trường dữ liệu (`field_index`):

#### Trường 1: Thời gian UTC (Giờ, Phút, Giây)
```c
      case 1: { // Ví dụ token: "123519"
        long raw_time = atol(token);
        packet->hour = (uint8_t)(raw_time / 10000);
        packet->minute = (uint8_t)((raw_time % 10000) / 100);
        packet->second = (uint8_t)(raw_time % 100);
        break;
      }
```
*   `raw_time` chuyển đổi từ chuỗi `"123519"` sang số nguyên `123519`.
*   Giờ (`hour`) lấy phần nguyên của phép chia cho 10000: $123519 / 10000 = 12$.
*   Phút (`minute`) lấy phần dư của phép chia cho 10000 rồi chia tiếp cho 100: $(123519 \% 10000) / 100 = 3519 / 100 = 35$.
*   Giây (`second`) lấy phần dư khi chia cho 100: $123519 \% 100 = 19$.

#### Trường 3 & 4: Vĩ độ (Latitude) và Hướng Vĩ độ (N/S)
```c
      case 3: { // Ví dụ token: "4807.038" tương ứng 48 độ 07.038 phút
        float raw_lat = atof(token);
        int degrees = (int)(raw_lat / 100);
        float minutes = raw_lat - (degrees * 100);
        packet->latitude = degrees + (minutes / 60.0f); // Đổi sang độ thập phân
        break;
      }
      case 4: { // Hướng vĩ độ
        if (token[0] == 'S')
          packet->latitude = -packet->latitude;
        break;
      }
```
*   Trong NMEA, vĩ độ có định dạng $DDMM.MMMM$ (Độ-Phút). Ta chia nguyên cho 100 để lấy phần Độ nguyên (`degrees`).
*   Phần Phút (`minutes`) là phần dư còn lại sau khi trừ đi phần Độ nguyên nhân với 100.
*   Quy đổi sang dạng độ thập phân (Decimal Degrees) để dễ tính toán trên bản đồ: $\text{Độ thập phân} = \text{Độ} + \frac{\text{Phút}}{60}$.
*   Nếu hướng vĩ độ là Nam (`S` - South), tọa độ sẽ được chuyển thành giá trị âm.

#### Trường 5 & 6: Kinh độ (Longitude) và Hướng Kinh độ (E/W)
```c
      case 5: { // Ví dụ token: "01131.000" tương ứng 11 độ 31.000 phút
        float raw_lon = atof(token);
        int degrees = (int)(raw_lon / 100);
        float minutes = raw_lon - (degrees * 100);
        packet->longitude = degrees + (minutes / 60.0f); // Đổi sang độ thập phân
        break;
      }
      case 6: { // Hướng kinh độ
        if (token[0] == 'W')
          packet->longitude = -packet->longitude;
        break;
      }
```
*   Tương tự như vĩ độ, kinh độ trong NMEA có định dạng $DDDMM.MMMM$. Sau khi quy đổi sang độ thập phân, nếu hướng kinh độ là Tây (`W` - West), tọa độ sẽ có giá trị âm.

#### Trường 7: Tốc độ di chuyển
```c
      case 7: { // Tốc độ đo bằng Knots (Hải lý/giờ)
        packet->speed_kmph = atof(token);
        break;
      }
```
*   Chuyển đổi chuỗi tốc độ thành số thực `float` và lưu vào thuộc tính `speed_kmph` của struct.

### 3.5. Kết thúc một trường để chuyển sang trường tiếp theo
```c
    if (next == NULL)
      break;
    current = next + 1;
    field_index++;
  }
```
*   Nếu đã chạm cuối chuỗi (`next == NULL`), thoát khỏi vòng lặp `while`.
*   Nếu chưa, gán con trỏ `current` dịch sang ký tự ngay sau dấu phẩy vừa tìm thấy (`next + 1`) và tăng chỉ số trường `field_index` thêm 1 đơn vị để xử lý trường tiếp theo.

---

## 4. Hàm tuần tuần tự hóa `serialize_gps_packet` (Dòng 91 - 97)

Hàm chuyển đổi toàn bộ cấu trúc dữ liệu struct nhị phân trong bộ nhớ máy tính thành một chuỗi Hexadecimal để truyền nhận dữ liệu.

```c
void serialize_gps_packet(const GPSPacket_t *packet, char *output_hex) {
  uint8_t *raw_ptr = (uint8_t *)packet;
  for (size_t i = 0; i < sizeof(GPSPacket_t); i++) {
    // In từng byte dưới dạng Hex 2 ký tự (in hoa) vào chuỗi
    sprintf(output_hex + (i * 2), "%02X", raw_ptr[i]);
  }
}
```

*   **`uint8_t *raw_ptr = (uint8_t *)packet;`**: Ép kiểu con trỏ struct thành con trỏ kiểu byte (`uint8_t*`). Điều này cho phép chúng ta duyệt qua từng byte thô cấu thành nên vùng nhớ của struct `packet`.
*   **`for (size_t i = 0; i < sizeof(GPSPacket_t); i++)`**: Lặp qua tất cả các byte trong struct (số lượng byte phụ thuộc vào kích thước thực tế của struct `GPSPacket_t` - khoảng 16 bytes).
*   **`sprintf(output_hex + (i * 2), "%02X", raw_ptr[i]);`**: 
    *   In giá trị của byte thứ `i` dưới dạng số Hex gồm 2 ký tự viết hoa (sử dụng định dạng `%02X`).
    *   Ghi trực tiếp kết quả vào vùng đệm `output_hex` tại vị trí dịch tương ứng là `i * 2` (do mỗi byte khi hiển thị dạng Hex sẽ cần đúng 2 ký tự).

---

## 5. Giải thích mã nguồn Python Logger `main.py` (Dòng 1 - 101)

File [main.py](file:///run/media/hungdp/New%20Volume/Coding/gps_telemetry_project/python_logger/main.py) là bộ tiếp nhận trung tâm của hệ thống. Nó chạy song song với chương trình C (kết nối qua cơ chế Pipe), đọc chuỗi dữ liệu Hex, giải mã, ghi nhật ký ra file CSV và tự động dựng bản đồ HTML trực quan hóa hành trình khi kết thúc.

### 5.1. Khởi tạo và thiết lập đường dẫn (Dòng 11 - 33)

```python
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_dir = os.path.join(project_root, "data")
    
    os.makedirs(data_dir, exist_ok=True)
    csv_file = os.path.join(data_dir, "gps_route.csv")
    map_file = os.path.join(data_dir, "vehicle_map.html")
```

*   **Đường dẫn tuyệt đối**: Sử dụng thư viện `os` để tính toán đường dẫn dựa vào vị trí của chính file `main.py` (`os.path.abspath(__file__)`). Cách làm này đảm bảo chương trình luôn tìm thấy thư mục lưu trữ `/data/` bất kể bạn chạy nó từ thư mục gốc nào của hệ thống.
*   **`os.makedirs(data_dir, exist_ok=True)`**: Tự động tạo thư mục `data/` ở thư mục gốc của dự án nếu thư mục này chưa tồn tại.
*   **Ghi tiêu đề CSV**: Chương trình kiểm tra sự tồn tại của file `gps_route.csv`. Nếu file chưa tồn tại, nó sẽ ghi hàng tiêu đề (header) bao gồm các trường: `Time_UTC`, `Latitude`, `Longitude`, `Speed_Knots`, và `Speed_KmH`.

### 5.2. Nhận dữ liệu qua đường ống Pipe (Dòng 36 - 68)

```python
        for line in sys.stdin:
            hex_data = line.strip()
            if not hex_data:
                continue

            gps_info = decode_hex_gps(hex_data)
```

*   **`sys.stdin`**: Chương trình Python đọc trực tiếp dữ liệu từ ngõ vào chuẩn (Standard Input). Khi kết nối Pipe (`./main.exe | python main.py`), tất cả những gì chương trình C `printf` ra màn hình sẽ được đưa trực tiếp vào luồng đầu vào này của Python theo thời gian thực.
*   **`line.strip()`**: Loại bỏ ký tự xuống dòng `\n` và khoảng trắng dư thừa ở đầu/cuối của chuỗi Hex nhận được.
*   **`decode_hex_gps(hex_data)`**: Gọi hàm giải mã từ file [decoder.py](file:///run/media/hungdp/New%20Volume/Coding/gps_telemetry_project/python_logger/decoder.py) để tách cấu trúc byte và chuyển đổi về dạng số thực/thời gian.

```python
                with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        gps_info['time'],
                        gps_info['latitude'],
                        gps_info['longitude'],
                        gps_info['speed_knots'],
                        gps_info['speed_kmh']
                    ])
                    f.flush()
```

*   **`mode='a'` (Append)**: Mở file CSV dưới chế độ ghi thêm. Mỗi tọa độ nhận được sẽ được ghi nối tiếp vào cuối file chứ không ghi đè mất dữ liệu cũ.
*   **`f.flush()`**: Ép buộc hệ điều hành ghi trực tiếp dữ liệu từ bộ đệm RAM xuống ổ đĩa cứng ngay lập tức. Điều này giúp ngăn ngừa mất mát dữ liệu hành trình trong trường hợp thiết bị giám sát bị tắt đột ngột hoặc mất nguồn.

### 5.3. Tạo bản đồ hành trình tương tác với Folium (Dòng 72 - 98)

Khi người dùng nhấn tổ hợp phím **`Ctrl + C`**, khối lệnh ngoại lệ `KeyboardInterrupt` sẽ được kích hoạt để dừng vòng lặp nhận dữ liệu và nhảy vào phần xử lý bản đồ `finally`.

```python
                import folium
                
                start_lat, start_lon = coordinate_history[0]
                my_map = folium.Map(location=[start_lat, start_lon], zoom_start=16)

                folium.PolyLine(coordinate_history, color="red", weight=4, opacity=0.8).add_to(my_map)

                folium.Marker(coordinate_history[0], popup="Start Route", icon=folium.Icon(color='green')).add_to(my_map)
                folium.Marker(coordinate_history[-1], popup="End Route", icon=folium.Icon(color='red')).add_to(my_map)

                my_map.save(map_file)
```

*   **`import folium`**: Chỉ import thư viện vẽ bản đồ Folium khi quá trình thu thập kết thúc (để tránh làm chậm thời gian khởi động ban đầu của ứng dụng).
*   **`folium.Map(...)`**: Khởi tạo một đối tượng bản đồ vệ tinh với điểm trung tâm là tọa độ đầu tiên (`coordinate_history[0]`) và mức phóng to khởi điểm (zoom) là 16.
*   **`folium.PolyLine(...)`**: Vẽ một đường nối (màu đỏ, độ dày nét vẽ là 4) đi qua toàn bộ danh sách tọa độ trong mảng lịch sử `coordinate_history` để trực quan hóa quãng đường xe đã đi qua.
*   **`folium.Marker(...)`**: Tạo hai mốc định vị trên bản đồ:
    *   **Điểm bắt đầu (Start Route)**: Có biểu tượng màu xanh lá cây (`green`).
    *   **Điểm kết thúc (End Route)**: Có biểu tượng màu đỏ (`red`).
*   **`my_map.save(map_file)`**: Lưu toàn bộ cấu trúc bản đồ tương tác sang một file HTML (`vehicle_map.html`). File này tích hợp sẵn bản đồ OpenStreetMap nên bạn chỉ cần mở trực tiếp bằng bất kỳ trình duyệt web nào (Chrome, Edge, Firefox) là có thể xem, phóng to, thu nhỏ và di chuyển bản đồ một cách sinh động.
