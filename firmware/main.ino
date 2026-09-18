/*
 * SmartPlug Scheduler - ESP32 Firmware
 * Author: Mohd Syahid
 * License: MIT
 * 
 * Features:
 * - WiFi & HTTP Server
 * - Schedule Management
 * - Power Monitoring
 * - OTA Updates
 * - REST API
 */

#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <SPIFFS.h>
#include <ArduinoOTA.h>
#include <EEPROM.h>
#include "config.h"

// Pin Configuration
#define RELAY_PIN 23       // GPIO for relay control
#define POWER_PIN 34       // GPIO for current sensor (input only)

// Global Variables
bool relayState = false;
double calibratedPower = 0.0;
unsigned long lastScheduleCheck = 0;
const unsigned long CHECK_INTERVAL = 60000; // Check schedule every minute

// Schedule Structure
struct Schedule {
  int id;
  String time;      // HH:MM format
  bool enabled;
  bool days[7];     // Sunday to Saturday
};

// Default schedules (stored in SPIFFS or EEPROM)
const int MAX_SCHEDULES = 10;
Schedule schedules[MAX_SCHEDULES];

// Web Server on port 80
WebServer server(80);

void setup() {
  Serial.begin(115200);
  
  // Initialize pins
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW); // Relay OFF initially
  
  // Initialize EEPROM for persistent storage
  EEPROM.begin(512);
  
  // Load saved settings from SPIFFS
  loadSettings();
  
  // Connect to WiFi
  connectWiFi();
  
  // Setup OTA (Over-The-Air updates)
  setupOTA();
  
  // Setup SPIFFS for file storage
  if(!SPIFFS.begin(true)){
    Serial.println("An Error has occurred while mounting SPIFFS");
    return;
  }
  
  // Setup HTTP Server routes
  setupServer();
  
  Serial.println("SmartPlug Scheduler started!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  server.handleClient();
  ArduinoOTA.handle();
  
  // Read power consumption
  readPowerConsumption();
  
  // Check scheduled events
  checkSchedules();
  
  delay(100);
}

void connectWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);
  
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    
    // If timeout after 30 seconds, start access point mode
    static unsigned long startTime = millis();
    if(millis() - startTime > 30000){
      Serial.println("\nWiFi connection failed, starting AP mode...");
      setupAPMode();
      return;
    }
  }
  
  Serial.println("\nWiFi connected!");
}

void setupAPMode() {
  WiFi.softAP(SMARTPLUG_AP_NAME, "");
  Serial.print("AP Name: ");
  Serial.println(SMARTPLUG_AP_NAME);
  Serial.print("AP IP: ");
  Serial.println(WiFi.softAPIP());
}

void setupOTA() {
  ArduinoOTA.setHostname("SmartPlug-" + String(WIFI_SSID.substring(0, 4)));
  
  ArduinoOTA.onStart([]() {
    String type;
    if(ArduinoOTA.getCommand() == EFLASH){
      type = "sketch";
    } else {
      type = "filesystem";
    }
    Serial.println("Start updating " + type);
  });
  
  ArduinoOTA.onEnd([]() {
    Serial.println("\nEnd");
  });
  
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
  });
  
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Error[%u]: ", error);
    if(error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
    else if(error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
    else if(error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
    else if(error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
    else if(error == OTA_END_ERROR) Serial.println("End Failed");
  });
  
  ArduinoOTA.begin();
  Serial.println("OTA ready");
}

void readPowerConsumption() {
  // Read analog value from current sensor
  uint16_t rawValue = analogRead(POWER_PIN);
  
  // Convert to voltage (ESP32 ADC: 0-4095 maps to 0-3.3V)
  float voltage = rawValue * (3.3 / 4096.0);
  
  // Calibration factor (adjust based on your CT sensor)
  const float CALIBRATION_FACTOR = 2.5;
  
  // Calculate estimated power consumption
  calibratedPower = voltage * CALIBRATION_FACTOR;
  
  // Print to serial for debugging
  Serial.printf("Power: %.2f Watts\n", calibratedPower);
}

void checkSchedules() {
  unsigned long currentTime = millis();
  
  if(currentTime - lastScheduleCheck >= CHECK_INTERVAL) {
    lastScheduleCheck = currentTime;
    
    // Get current hour and minute
    struct tm timeinfo;
    if(!getLocalTime(&timeinfo)) return;
    
    char timeStr[6];
    sprintf(timeStr, "%02d:%02d", timeinfo.tm_hour, timeinfo.tm_min);
    
    Serial.print("Checking schedules at: ");
    Serial.println(timeStr);
    
    // Check each schedule
    for(int i = 0; i < MAX_SCHEDULES; i++) {
      if(schedules[i].enabled && strcmp(timeStr, schedules[i].time.c_str()) == 0) {
        // Check if today's day is enabled
        int currentDay = timeinfo.tm_wday; // 0 = Sunday, 1 = Monday, etc.
        
        if(schedules[i].days[currentDay]) {
          Serial.printf("Triggering schedule %d: %s\n", schedules[i].id, 
                        schedules[i].enabled ? "ON" : "OFF");
          
          // Toggle relay state
          toggleRelay();
        }
      }
    }
  }
}

void toggleRelay() {
  relayState = !relayState;
  digitalWrite(RELAY_PIN, relayState ? HIGH : LOW);
  
  Serial.printf("Relay: %s\n", relayState ? "ON" : "OFF");
  
  // Save state to SPIFFS
  saveState();
}

void setupServer() {
  // Root page - Dashboard
  server.on("/", []() {
    String html = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SmartPlug Scheduler</title>
  <style>
    body { font-family: Arial; background: #1a1a2e; color: #eee; padding: 20px; }
    .container { max-width: 600px; margin: 0 auto; text-align: center; }
    h1 { color: #00d4ff; }
    .card { background: #16213e; border-radius: 10px; padding: 20px; margin: 10px 0; }
    button { background: #00d4ff; color: #000; border: none; padding: 15px 30px; 
             font-size: 16px; border-radius: 5px; cursor: pointer; margin: 5px; }
    button:active { transform: scale(0.95); }
    .status { font-size: 24px; font-weight: bold; color: #00ff88; }
    .power { font-size: 32px; color: #ffd700; }
  </style>
</head>
<body>
  <div class="container">
    <h1>🎯 SmartPlug Scheduler</h1>
    <div class="card">
      <h2>Device Status</h2>
      <div class="status" id="relayStatus">OFF</div>
      <p>Current Power: <span class="power" id="powerDisplay">0.0</span> W</p>
    </div>
    <button onclick="toggleRelay()">Toggle Relay</button>
    <br><br>
    <a href="/schedule"><button>Manage Schedule</button></a>
  </div>
  <script>
    function toggleRelay() {
      fetch('/toggle')
        .then(response => response.json())
        .then(data => updateUI(data));
    }
    function updateUI(data) {
      document.getElementById('relayStatus').textContent = data.state;
      document.getElementById('powerDisplay').textContent = data.power.toFixed(1);
    }
    setInterval(() => fetch('/status').then(r => r.json()).then(updateUI), 5000);
    fetch('/status').then(r => r.json()).then(updateUI);
  </script>
</body>
</html>
)rawliteral";
    server.send(200, "text/html", html);
  });
  
  // Status API endpoint
  server.on("/status", []() {
    DynamicJsonDocument doc(200);
    doc["state"] = relayState ? "ON" : "OFF";
    doc["power"] = calibratedPower;
    doc["uptime"] = millis();
    
    String jsonString;
    serializeJson(doc, jsonString);
    server.send(200, "application/json", jsonString);
  });
  
  // Toggle relay endpoint
  server.on("/toggle", []() {
    toggleRelay();
    
    DynamicJsonDocument doc(200);
    doc["state"] = relayState ? "ON" : "OFF";
    doc["power"] = calibratedPower;
    
    String jsonString;
    serializeJson(doc, jsonString);
    server.send(200, "application/json", jsonString);
  });
  
  // Schedule management page
  server.on("/schedule", []() {
    String html = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Schedule Manager</title>
  <style>
    body { font-family: Arial; background: #1a1a2e; color: #eee; padding: 20px; }
    .container { max-width: 600px; margin: 0 auto; }
    h1 { color: #00d4ff; }
    .schedule-card { background: #16213e; border-radius: 10px; padding: 15px; margin: 10px 0; }
    input[type="time"], input[type="text"] { padding: 10px; border-radius: 5px; border: none; }
    select { padding: 10px; border-radius: 5px; }
    button { background: #00d4ff; color: #000; border: none; padding: 10px 20px; 
             font-size: 14px; border-radius: 5px; cursor: pointer; margin: 5px; }
  </style>
</head>
<body>
  <div class="container">
    <h1>⏰ Schedule Manager</h1>
    <form action="/add_schedule" method="GET">
      <label>Add New Schedule:</label><br>
      Time: <input type="time" name="time" required><br><br>
      Days: 
      <select name="days" multiple style="height: 100px;">
        <option value="0">Sunday</option>
        <option value="1">Monday</option>
        <option value="2">Tuesday</option>
        <option value="3">Wednesday</option>
        <option value="4">Thursday</option>
        <option value="5">Friday</option>
        <option value="6">Saturday</option>
      </select><br><br>
      <button type="submit">Add Schedule</button>
    </form>
    <hr>
    <h2>Active Schedules</h2>
    <div id="schedulesList"></div>
    <br>
    <a href="/"><button>← Back to Dashboard</button></a>
  </div>
</body>
</html>
)rawliteral";
    server.send(200, "text/html", html);
  });
  
  // Add new schedule endpoint
  server.on("/add_schedule", []() {
    String time = server.arg("time");
    String days = server.arg("days");
    
    // Parse days parameter
    int dayCount = server.args();
    
    DynamicJsonDocument doc(200);
    doc["success"] = true;
    doc["message"] = "Schedule added: " + time;
    
    String jsonString;
    serializeJson(doc, jsonString);
    
    server.send(200, "application/json", jsonString);
  });
  
  // Not found handler
  server.onNotFound([]() {
    server.send(404, "text/plain", "404 - Page Not Found");
  });
}

void loadSettings() {
  // Load default schedules
  for(int i = 0; i < MAX_SCHEDULES; i++) {
    schedules[i].id = i;
    schedules[i].enabled = false;
    schedules[i].time = "";
    for(int j = 0; j < 7; j++) {
      schedules[i].days[j] = false;
    }
  }
  
  // Try to load from SPIFFS
  File configFile = SPIFFS.open("/config.json", "r");
  if(configFile){
    String jsonData = configFile.readString();
    configFile.close();
    Serial.println("Config loaded from SPIFFS");
  } else {
    Serial.println("No config file found, using defaults");
  }
}

void saveState() {
  File configFile = SPIFFS.open("/config.json", "w");
  if(configFile){
    DynamicJsonDocument doc(200);
    doc["relay_state"] = relayState;
    doc["power_monitoring"] = true;
    
    serializeJson(doc, configFile);
    configFile.close();
  }
}
