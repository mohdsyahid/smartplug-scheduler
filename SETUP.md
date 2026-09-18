# SmartPlug Scheduler - Setup Guide 📚

Panduan lengkap untuk memasang dan menggunakan SmartPlug Scheduler.

## Prerequisites 🔧

### Hardware:
- ESP32 Development Board (NodeMCU-32S, DOIT ESP32, dll)
- Relay Module 5V 1-channel
- CT Current Transformer Sensor (contoh: AC20, SCPHCL)
- Breadboard & Jumper wires
- Computer dengan USB cable

### Software:
- Arduino IDE (untuk flash firmware ke ESP32)
- Python 3.8+ (untuk backend server)
- Git (optional, untuk version control)

---

## Installation Step-by-Step 📋

### Part 1: Flash Firmware ke ESP32

#### Step 1: Install Arduino IDE
1. Download Arduino IDE dari: https://www.arduino.cc/en/software
2. Install pada computer anda
3. Launch Arduino IDE

#### Step 2: Add ESP32 Board Support
1. Open Arduino IDE
2. Go to **File → Preferences**
3. In "Additional Board Manager URLs", add:
   ```
   http://arduino.esp8266.com/stable/package_esp8266com_index.json
   http://dl.espressif.com/dl/package_esp32_index.json
   ```
4. Click **OK**
5. Go to **Tools → Board → Boards Manager**
6. Search for "ESP32"
7. Install package by Espressif Systems

#### Step 3: Download & Configure Code
1. Copy folder `firmware` from this repository
2. Open `main.ino` dalam Arduino IDE
3. Edit `config.h`:
   ```cpp
   const char* WIFI_SSID = "nama_wifi_anda";
   const char* WIFI_PASSWORD = "password_wifi_anda";
   ```

#### Step 4: Upload Code
1. Select board: **Tools → Board → DOIT ESP32 DEVKIT V1**
2. Select port: **Tools → Port → COMx** (Windows) / `/dev/ttyUSB0` (Linux)
3. Click **Upload** button (arrow icon)
4. Wait for "Upload Done!" message

### Part 2: Hardware Wiring 🔌

```
ESP32 DevKit          Relay Module        CT Sensor
─────────────────     ───────────────     ───────────
       5V    ────────> VCC               │
       GND   ────────> GND               │
GPIO 23 (D12) ───────> IN                │
                                SENSE ───> GPIO 34 (AN0)
                                   GND   ───> GND
```

**Wiring Notes:**
- Relay module controls the power circuit
- CT sensor clips around live wire of the load
- Never connect high voltage directly to ESP32!

### Part 3: Test Connection

#### Method 1: Serial Monitor
1. Connect ESP32 via USB
2. Open Serial Monitor (Ctrl+Shift+M)
3. Set baud rate to **115200**
4. You should see:
   ```
   Connecting to WiFi: YOUR_WIFI_NAME
   WiFi connected!
   IP Address: 192.168.1.XXX
   SmartPlug Scheduler started!
   ```

#### Method 2: Web Interface
1. Find ESP32 IP from Serial Monitor
2. Type IP address in browser
3. Dashboard should appear

### Part 4: Backend Server Setup

#### Step 1: Navigate to Backend Folder
```bash
cd smartplug-scheduler/backend
```

#### Step 2: Create Virtual Environment (Recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Run Server
```bash
python server.py
```

Output should show:
```
Initializing SmartPlug Scheduler Backend...
Database initialized!
Starting server on http://localhost:5000
 * Running on http://0.0.0.0:5000
```

#### Step 5: Access Dashboard
Open browser and go to:
- Local: http://localhost:5000
- Network: http://YOUR_IP:5000

### Part 5: Android App (Optional)

#### Option A: Use Pre-built APK
(Download from releases if available)

#### Option B: Build from Source

**Prerequisites:**
- Android Studio Arctic Fox or later
- Java Development Kit (JDK) 11+

**Steps:**
```bash
cd smartplug-scheduler/frontend/android
./gradlew assembleDebug
```

APK will be generated at:
`app/build/outputs/apk/debug/app-debug.apk`

Install via USB debugging or sideloading.

---

## Configuration Guide ⚙️

### 1. Calibrate Power Sensor

To get accurate power readings:

```python
# In main.ino, adjust CALIBRATION_FACTOR:
const float CALIBRATION_FACTOR = 2.5; // Change this value
```

**Calibration Steps:**
1. Plug in device with known wattage (e.g., 100W bulb)
2. Read power value from Serial Monitor
3. Calculate new factor:
   ```
   New Factor = (Known Wattage / Measured Value) * Current Factor
   ```
4. Update config.h and re-upload

### 2. Set Default State on Boot

In `main.ino`, modify:
```cpp
bool relayState = false;  // false = OFF, true = ON after boot
```

### 3. Modify Timer Check Interval

In `main.ino`:
```cpp
const unsigned long CHECK_INTERVAL = 60000; // 60 seconds
```

Change to desired interval in milliseconds.

### 4. Schedule Management

**Via Web UI:**
1. Login to dashboard
2. Navigate to "Schedule Manager"
3. Click "Add Schedule"
4. Set time and days

**Via API:**
```bash
curl -X POST http://localhost:5000/api/schedules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Turn off lights",
    "start_time": "23:00",
    "end_time": "23:30",
    "device_id": 1,
    "daysOfWeek": 127
  }'
```

---

## Troubleshooting 🔍

### Problem: ESP32 won't connect to WiFi

**Solution:**
1. Check WiFi credentials in `config.h`
2. Ensure WiFi supports 2.4GHz (not 5GHz)
3. Verify password is correct (case-sensitive)
4. Try resetting ESP32 by pressing BOOT button

### Problem: Power readings are inaccurate

**Solution:**
1. Calibrate CT sensor using guide above
2. Check wiring connections
3. Ensure CT sensor is properly clamped
4. Remove other electrical interference

### Problem: Backend server won't start

**Solution:**
1. Check port 5000 is not in use:
   ```bash
   netstat -an | findstr :5000
   ```
2. Try different port in `server.py`:
   ```python
   app.run(host='0.0.0.0', port=8080, debug=True)
   ```
3. Verify Python dependencies installed

### Problem: OTA Updates fail

**Solution:**
1. Ensure both ESP32 and computer on same WiFi network
2. Check firewall settings allow port 8266
3. Restart Arduino IDE before uploading

---

## Advanced Features 🚀

### 1. MQTT Integration

Add to `main.ino`:
```cpp
#include <PubSubClient.h>

WiFiClient espClient;
PubSubClient mqtt(espClient);

void setupMQTT() {
  mqtt.connect("smartplug", username, password);
}
```

### 2. Home Assistant Integration

Home Assistant automatically discovers ESP32 devices via SSDP/mDNS.

Add configuration to `configuration.yaml`:
```yaml
mqtt:
  - sensor:
      - name: "SmartPlug Power"
        state_topic: "smartplug/power"
```

### 3. Google Assistant/Alexa Integration

Use IFTTT or Node-RED to connect SmartPlug API to voice assistants.

---

## Security Considerations 🔒

1. **Always change default WiFi credentials**
2. **Enable HTTPS** for production deployment
3. **Use strong passwords** in admin panel
4. **Regular firmware updates** for security patches
5. **Network isolation** - put IoT devices on separate VLAN

---

## Backup & Restore 🔄

### Backup Settings
1. Access `/backup` endpoint in API
2. Save JSON file containing all configurations

### Restore Settings
```bash
curl -X POST http://localhost:5000/api/backup/restore \
  -F "file=@backup.json"
```

---

## Useful Commands 📝

### Reset ESP32 to Factory Defaults
Press RESET button twice quickly during boot

### Clear SPIFFS Storage
```cpp
SPIFFS.format();
```

### View Current Config
Visit: `http://ESP32_IP/config`

### Get System Stats
Visit: `http://ESP32_IP/stats`

---

## Support & Contact 💬

- GitHub Issues: [Your Repo]/issues
- Email: mohdsyahid@email.com
- Telegram: [@yourhandle](https://t.me/yourhandle)

**Happy automating! 🎯✨**
