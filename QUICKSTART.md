# SmartPlug Scheduler - Quick Start Guide 🚀

Panduan pantas untuk memulakan project dalam 5 minit!

## Step 1: Flash Firmware ke ESP32 ⏱️ (2 minit)

### Prerequisites:
- Arduino IDE installed
- ESP32 Board Manager added

### Commands:
```bash
# 1. Open Arduino IDE
arduino

# 2. Install ESP32 Board Support
Tools → Board Manager → Search "ESP32" → Install

# 3. Load firmware
File → Open → smartplug-scheduler/firmware/main.ino

# 4. Edit WiFi credentials in config.h
const char* WIFI_SSID = "your_wifi";
const char* WIFI_PASSWORD = "your_password";

# 5. Upload
Tools → Board → DOIT ESP32 DEVKIT V1
Tools → Port → COMx
Click Upload button
```

✅ **Success indicator:** Serial Monitor shows IP address

---

## Step 2: Build Hardware 🔌 (10-15 minit)

### Required Parts:
- [ ] ESP32 DevKit
- [ ] Relay Module (5V)
- [ ] CT Current Sensor
- [ ] Breadboard & Jumper wires

### Wiring:
```
ESP32          Relay       CT Sensor
─────────      ───────     ─────────
5V    ───────> VCC        │
GND   ───────> GND        │
D23   ───────> IN         │
                        SENSE ──> D34
```

✅ **Test:** LED on relay module should click when you toggle device from web UI

---

## Step 3: Setup Backend Server 💻 (1 minit)

### Commands:
```bash
cd smartplug-scheduler/backend

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run server
python server.py
```

✅ **Success indicator:** Console shows "Running on http://0.0.0.0:5000"

---

## Step 4: Access Dashboard 🌐 (30 seconds)

### Options:

**Option A: Direct ESP32 Web Interface**
```
http://[ESP32_IP]
```

**Option B: Full Backend Dashboard**
```
http://localhost:5000
```

✅ **Should see:** Beautiful dashboard with device status and controls

---

## Step 5: Test Everything ✅

### Checklist:
- [ ] ESP32 connects to WiFi
- [ ] Can access web dashboard
- [ ] Toggle button works
- [ ] Power readings show accurate values
- [ ] Backend server running
- [ ] Android app (if built) connected

### Quick Tests:

```bash
# Test ESP32 status endpoint
curl http://[ESP32_IP]/status

# Test backend API
curl http://localhost:5000/api/devices

# Test power monitoring
watch -n 5 'curl http://[ESP32_IP]/status'
```

---

## Next Steps 🎯

### Customize:
1. **Change WiFi credentials** in `firmware/config.h`
2. **Calibrate power sensor** using guide in SETUP.md
3. **Add more devices** through backend API

### Deploy:
1. Purchase hardware components
2. Build multiple units
3. Set up cloud backend (AWS/GCP/Azure)
4. Deploy to production

---

## Common Issues & Fixes

### Issue: ESP32 won't connect to WiFi
**Fix:** Check SSID/password is correct, ensure 2.4GHz WiFi

### Issue: Backend server won't start
**Fix:** Make sure port 5000 not in use: `netstat -an | findstr :5000`

### Issue: Power readings wrong
**Fix:** Calibrate using formula in SETUP.md

---

## Need Help? 🤔

- Full documentation: [SETUP.md](SETUP.md)
- API reference: [docs/API.md](docs/API.md)
- Hardware guide: [hardware/BOM.md](hardware/BOM.md)
- GitHub Issues: https://github.com/YOUR_USERNAME/smartplug-scheduler/issues

---

**Congratulations! Your SmartPlug Scheduler is now live! 🎉**

Built with ❤️ for the Malaysian IoT community
