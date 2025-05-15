#include <Wire.h>
#include <Adafruit_ADS1X15.h>

// Row MUX control pins (via MOSFETs or direct GPIOs)
#define ROW_MUX_S0 27
#define ROW_MUX_S1 26
#define ROW_MUX_S2 33
#define ROW_MUX_S3 14  // GPIO14 — we’ll treat this carefully

// Column MUX control pins
#define COL_MUX_S0 25
#define COL_MUX_S1 32
#define COL_MUX_S2 13
#define COL_MUX_S3 12  // (not used in 4-column setup)

Adafruit_ADS1115 ads;
uint16_t sensor_data[64]; // 16 rows × 4 columns

// MUX channel selection helper
void setMuxChannel(uint8_t s0, uint8_t s1, uint8_t s2, uint8_t s3, uint8_t channel) {
  digitalWrite(s0, (channel >> 0) & 1);
  digitalWrite(s1, (channel >> 1) & 1);
  digitalWrite(s2, (channel >> 2) & 1);
  digitalWrite(s3, (channel >> 3) & 1);
  delayMicroseconds(20);  // MUX settling time
}

void setup() {
  Serial.begin(115200);
  Wire.begin();

  if (!ads.begin()) {
    Serial.println("Failed to initialize ADS1115!");
    while (1);
  }

  ads.setGain(GAIN_ONE);  // ±4.096V
  ads.setDataRate(RATE_ADS1115_860SPS);  // Fastest sample rate

  // Init row MUX control pins
  pinMode(ROW_MUX_S0, OUTPUT);
  pinMode(ROW_MUX_S1, OUTPUT);
  pinMode(ROW_MUX_S2, OUTPUT);
  pinMode(ROW_MUX_S3, OUTPUT);  // Important for GPIO14

  // Force GPIO14 LOW once to ensure it’s not floating high
  digitalWrite(ROW_MUX_S3, LOW);
  delay(10);  // Allow it to settle

  // Init column MUX control pins
  pinMode(COL_MUX_S0, OUTPUT);
  pinMode(COL_MUX_S1, OUTPUT);
  pinMode(COL_MUX_S2, OUTPUT);
  pinMode(COL_MUX_S3, OUTPUT);
}

void loop() {
  for (int row = 0; row < 16; row++) {
    setMuxChannel(ROW_MUX_S0, ROW_MUX_S1, ROW_MUX_S2, ROW_MUX_S3, row);

    Serial.print("Row ");
    Serial.print(row);
    Serial.print(": ");

    for (int col = 0; col < 4; col++) {
      setMuxChannel(COL_MUX_S0, COL_MUX_S1, COL_MUX_S2, COL_MUX_S3, col);
      delayMicroseconds(50);  // Let signal settle
      sensor_data[row * 4 + col] = ads.readADC_SingleEnded(1);  // A1 of ADS1115
      Serial.print(sensor_data[row * 4 + col]);
      Serial.print(" ");
    }
    Serial.println();
  }

  Serial.println("----");
  delay(1);  // Keeps overall update rate ~1000 Hz
}
