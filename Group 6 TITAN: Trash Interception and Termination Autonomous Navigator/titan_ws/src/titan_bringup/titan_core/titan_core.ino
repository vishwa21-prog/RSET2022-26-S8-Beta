#include <Wire.h>

/*
 * TITAN-Core Firmware v1.0
 * Reverted to original odometry-only telemetry (11-byte packet)
 */

// --- HARDWARE PINOUT ---
#define PIN_R_PWM_F 6
#define PIN_R_PWM_B 11
#define PIN_L_PWM_F 9
#define PIN_L_PWM_B 10

#define PIN_ENC_R_A 2 
#define PIN_ENC_R_B 4
#define PIN_ENC_L_A 3
#define PIN_ENC_L_B 5
// -----------------------

volatile long left_ticks = 0;
volatile long right_ticks = 0;

unsigned long last_cmd_time = 0;
const unsigned long WATCHDOG_TIMEOUT = 500; // ms

void setup() {
  Serial.begin(115200);
  
  pinMode(PIN_L_PWM_F, OUTPUT); pinMode(PIN_L_PWM_B, OUTPUT);
  pinMode(PIN_R_PWM_F, OUTPUT); pinMode(PIN_R_PWM_B, OUTPUT);
  
  pinMode(PIN_ENC_L_A, INPUT_PULLUP); pinMode(PIN_ENC_L_B, INPUT_PULLUP);
  pinMode(PIN_ENC_R_A, INPUT_PULLUP); pinMode(PIN_ENC_R_B, INPUT_PULLUP);
  
  attachInterrupt(digitalPinToInterrupt(PIN_ENC_L_A), handleL, RISING);
  attachInterrupt(digitalPinToInterrupt(PIN_ENC_R_A), handleR, RISING);
}

void loop() {
  if (Serial.available() >= 7) {
    if (Serial.read() == 0xAA && Serial.read() == 0x55) {
      int16_t pwm_l = (int16_t)((Serial.read() << 8) | Serial.read());
      int16_t pwm_r = (int16_t)((Serial.read() << 8) | Serial.read());
      uint8_t crc = Serial.read();
      
      if (((pwm_l ^ pwm_r) & 0xFF) == crc) {
        setMotors(pwm_l, pwm_r);
        last_cmd_time = millis();
      }
    }
  }

  if (millis() - last_cmd_time > WATCHDOG_TIMEOUT) {
    setMotors(0, 0);
  }

  static unsigned long last_telemetry = 0;
  if (millis() - last_telemetry > 20) {
    sendTelemetry();
    last_telemetry = millis();
  }
}

void setMotors(int l, int r) {
  l = constrain(l, -255, 255);
  r = constrain(r, -255, 255);

  if (l >= 0) { analogWrite(PIN_L_PWM_F, l); analogWrite(PIN_L_PWM_B, 0); }
  else { analogWrite(PIN_L_PWM_F, 0); analogWrite(PIN_L_PWM_B, abs(l)); }
  
  if (r >= 0) { analogWrite(PIN_R_PWM_F, r); analogWrite(PIN_R_PWM_B, 0); }
  else { analogWrite(PIN_R_PWM_F, 0); analogWrite(PIN_R_PWM_B, abs(r)); }
}

void sendTelemetry() {
  Serial.write(0xAA);
  Serial.write(0x55);
  
  // Pack 4-byte ticks
  byte* l_ptr = (byte*)&left_ticks;
  byte* r_ptr = (byte*)&right_ticks;
  for (int i = 3; i >= 0; i--) Serial.write(l_ptr[i]);
  for (int i = 3; i >= 0; i--) Serial.write(r_ptr[i]);
  
  uint8_t crc = (uint8_t)(left_ticks ^ right_ticks);
  Serial.write(crc);
}

void handleL() {
  if (digitalRead(PIN_ENC_L_B) == HIGH) left_ticks++;
  else left_ticks--;
}

void handleR() {
  if (digitalRead(PIN_ENC_R_B) == HIGH) right_ticks++;
  else right_ticks--;
}
