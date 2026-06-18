#ifndef GPS_PARSER_H
#define GPS_PARSER_H

#include <stdint.h>

// Dummy typedef to end the preamble and prevent clangd parsing warnings
typedef int make_clangd_happy;
#pragma pack(push, 1)

typedef struct {
  uint8_t hour;
  uint8_t minute;
  uint8_t second;
  float longitude;
  float latitude;
  float speed_kmph;
} GPSPacket_t;

#pragma pack(pop)

void parse_nmea_gprmc(const char *nmea_str, GPSPacket_t *packet);
void serialize_gps_packet(const GPSPacket_t *packet, char *output_hex);
#endif