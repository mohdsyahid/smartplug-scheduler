/*
 * SmartPlug Scheduler - Configuration Header
 * Modify these values according to your setup
 */

#ifndef CONFIG_H
#define CONFIG_H

// WiFi Credentials
const char* WIFI_SSID = "YOUR_WIFI_NAME";        // Ganti dengan nama WiFi anda
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"; // Ganti dengan password WiFi

// Access Point Name (when WiFi connection fails)
const char* SMARTPLUG_AP_NAME = "SmartPlug_Setup";

// Pin Definitions
#define RELAY_PIN 23         // GPIO 23 untuk relay (controllable output)
#define POWER_PIN 34         // GPIO 34 untuk current sensor (input only!)

// Power Sensor Calibration
// Adjust these values based on your CT sensor model
const float CALIBRATION_FACTOR = 2.5;           // Faktor kalibrasi (sesuaikan nilai sebenar)
const float VOLTAGE_OFFSET = 1.65;              // Voltage offset (half of reference voltage)
const int ADC_RESOLUTION = 12;                  // ESP32 ADC resolution (0-4095)

// Network Settings
const unsigned long CHECK_INTERVAL = 60000;     // Interval semakan schedule (dalam ms)
const unsigned long HEARTBEAT_INTERVAL = 30000; // Heartbeat interval (dalam ms)

// Maximum number of schedules supported
const int MAX_SCHEDULES = 10;

// Web Interface Settings
const char* WEB_TITLE = "SmartPlug Scheduler";
const int SERVER_PORT = 80;

// Serial Debugging
#define DEBUG_ENABLED true
#if DEBUG_ENABLED
  #define DEBUG_PRINT(x) Serial.print(x)
  #define DEBUG_PRINTLN(x) Serial.println(x)
  #define DEBUG_PRINTF(fmt, args...) Serial.printf(fmt, ##args)
#else
  #define DEBUG_PRINT(x) ((void)0)
  #define DEBUG_PRINTLN(x) ((void)0)
  #define DEBUG_PRINTF(fmt, args...) ((void)0)
#endif

// LED Indicator
#define STATUS_LED_PIN 2   // GPIO 2 untuk LED status (built-in LED pada kebanyakan ESP32)

#endif // CONFIG_H
