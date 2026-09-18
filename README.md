# SmartPlug Scheduler 🎯🔌

Sistem kawalan enamel pintar (smart plug) menggunakan ESP32 dengan keupayaan jadual masa automatik dan monitoring penggunaan tenaga.

## 🚀 Features

- ⏰ **Timer Scheduler** - Set jadual masa untuk on/off automatable
- 📱 **Android Control** - Aplikasi Android untuk kawalan manual
- 🔌 **Power Monitoring** - Pantau penggunaan tenaga secara real-time
- 💾 **Data Logging** - Simpan data penggunaan tenaga
- 🔄 **OTA Updates** - Update firmware tanpa kabel
- 📊 **Dashboard Web** - Dashboard untuk lihat statistics

## 🛠️ Hardware Required

### Components:
1. ESP32 Development Board (NodeMCU-32S atau DFRobot FireBeetle 2 ESP32)
2. Relay Module (5V 1-channel)
3. CT Current Transformer Sensor (AC20 atau SCPHCL)
4. Power supply 5V untuk relay (optional jika ESP32 provide power)
5. Breadboard & Jumper wires

### Wiring Diagram:

```
ESP32          Relay Module      CT Sensor
GPIO 23 ──────> IN               │
5V    ────────> VCC              │
GND   ────────> GND              │
                         SENSE OUT ───> GPIO 34 (Analog)
```

### Physical Setup:
```
┌─────────────────────────────────────┐
│        Wall Outlet                  │
│    ┌─────────┐                      │
│    │  PLUG   │ ───────┬─────┐       │
│    └─────────┘        │     │       │
│                       │     │       │
│                   ┌───┴┐  [CT]       │
│                   │RLY│  SENSOR     │
│                   └─┬─┘             │
│                     │               │
│                ┌────┴────┐          │
│                │  LOAD   │          │
│                │DEVICE   │          │
│                └─────────┘          │
└─────────────────────────────────────┘
```

## 📦 Installation

### 1. Flash Firmware ke ESP32

#### Prerequisites:
- Arduino IDE atau PlatformIO
- ESP32 Board support untuk Arduino IDE

#### Steps:
1. Buka folder `firmware/` dalam Arduino IDE
2. Pilih board: Tools → Board → "DOIT ESP32 DEVKIT V1"
3. Select port: Tools → Port → COMx (Windows) /dev/ttyUSB0 (Linux)
4. Upload code ke ESP32

### 2. Setup Backend Server

```bash
cd backend
pip install -r requirements.txt
python server.py
```

Backend akan running di `http://localhost:5000`

### 3. Install Android App

Download APK dari releases atau build dari source:

```bash
cd frontend/android
./gradlew assembleDebug
```

APK akan berada di `app/build/outputs/apk/debug/app-debug.apk`

## 📖 Usage Guide

### Setting Timer Schedule

Via Android App:
1. Connect ke ESP32 WiFi network (SmartPlug_XXXX)
2. Open app → Dashboard
3. Tap "Add Schedule"
4. Set time and repeat days
5. Save

Via Web Interface (setelah connect):
- Access URL IP ESP32 melalui browser
- Navigate ke "Schedule" tab
- Add new schedule

### View Power Consumption

- Android app shows real-time wattage
- Historical data available in dashboard
- Weekly/Monthly reports generated automatically

## 🔧 Configuration

### ESP32 WiFi Credentials

Edit `firmware/config.h`:
```cpp
const char* WIFI_SSID = "your_wifi_name";
const char* WIFI_PASS = "your_wifi_password";
```

### Calibration (Power Measurement)

```python
# In calibration mode, adjust calibration factor
calibration_factor = measured_value / actual_wattage
```

## 📁 Project Structure

```
smartplug-scheduler/
├── firmware/           # ESP32 Arduino code
│   ├── main.ino
│   ├── config.h
│   └── schedules.cpp
├── backend/            # Python Flask server
│   ├── server.py
│   ├── requirements.txt
│   └── database.db
├── frontend/           # Android & web apps
│   ├── android/
│   ├── web-dashboard/
│   └── flutter-app/
├── hardware/           # Hardware docs
│   ├── wiring-diagram.pdf
│   └── bom.csv
└── docs/               # Documentation
    ├── setup-guide.md
    └── api-docs.md
```

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

## 📄 License

This project is licensed under MIT License - see LICENSE file for details.

## 🙏 Credits

- ESP32 by Espressif Systems
- Designed for Malaysian smart home enthusiasts
- Inspired by Home Assistant ecosystem

## 📞 Support

GitHub Issues: https://github.com/YOUR_USERNAME/smartplug-scheduler/issues

---
Built with ❤️ in Malaysia