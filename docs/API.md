# SmartPlug Scheduler - API Documentation 📡

## Base URL
```
http://localhost:5000/api
```

---

## Endpoints

### Devices Management

#### Get All Devices
**Endpoint:** `GET /api/devices`

**Response:**
```json
[
  {
    "id": 1,
    "name": "Living Room Plug",
    "mac_address": "AA:BB:CC:DD:EE:FF",
    "state": "on",
    "created_at": "2024-01-15 10:30:00"
  }
]
```

#### Create Device
**Endpoint:** `POST /api/devices`

**Request Body:**
```json
{
  "name": "Bedroom Lamp",
  "mac_address": "11:22:33:44:55:66"
}
```

**Response:**
```json
{
  "id": 2,
  "name": "Bedroom Lamp",
  "mac_address": "11:22:33:44:55:66",
  "state": "off"
}
```

#### Toggle Device State
**Endpoint:** `POST /api/devices/{device_id}/toggle`

**Response:**
```json
{
  "id": 1,
  "name": "Living Room Plug",
  "state": "on"
}
```

#### Get Single Device
**Endpoint:** `GET /api/devices/{device_id}`

**Response:**
```json
{
  "id": 1,
  "name": "Living Room Plug",
  "mac_address": "AA:BB:CC:DD:EE:FF",
  "state": "on",
  "created_at": "2024-01-15 10:30:00"
}
```

---

### Schedule Management

#### Get All Schedules
**Endpoint:** `GET /api/schedules`

**Response:**
```json
[
  {
    "id": 1,
    "device_id": 1,
    "name": "Turn off lights",
    "start_time": "23:00",
    "end_time": "23:30",
    "daysOfWeek": 127,
    "enabled": 1,
    "created_at": "2024-01-15 10:35:00"
  }
]
```

#### Create Schedule
**Endpoint:** `POST /api/schedules`

**Request Body:**
```json
{
  "name": "Morning Routine",
  "start_time": "07:00",
  "end_time": "07:30",
  "device_id": 1,
  "daysOfWeek": 64,
  "enabled": 1
}
```

**Note:** daysOfWeek bitmask:
- Bit 0 (1) = Sunday
- Bit 1 (2) = Monday  
- Bit 2 (4) = Tuesday
- Bit 3 (8) = Wednesday
- Bit 4 (16) = Thursday
- Bit 5 (32) = Friday
- Bit 6 (64) = Saturday

Examples:
- 127 = Every day (all bits set)
- 64 = Mon-Fri only (binary: 1000000)
- 96 = Weekends only (binary: 1100000)

---

### Power Monitoring

#### Get Device History
**Endpoint:** `GET /api/devices/{device_id}/history?limit=50`

**Query Parameters:**
- `limit` (optional): Number of records to return (default: 50)

**Response:**
```json
[
  {
    "id": 1,
    "device_id": 1,
    "power_watts": 150.5,
    "timestamp": "2024-01-15 10:40:00"
  },
  {
    "id": 2,
    "device_id": 1,
    "power_watts": 0.0,
    "timestamp": "2024-01-15 10:45:00"
  }
]
```

#### Get Daily Statistics
**Endpoint:** `GET /api/stats/daily`

**Response:**
```json
{
  "date": "2024-01-15",
  "total_watts": 3600.75,
  "average_watts": 150.03,
  "readings_count": 24
}
```

---

### Real-time ESP32 Interface

#### Web Dashboard (ESP32 Internal Server)
**Endpoint:** `http://{ESP32_IP}/`

Access web interface directly from ESP32 without backend.

**Endpoints:**
- `/` - Main dashboard
- `/status` - JSON status response
- `/toggle` - Toggle relay state
- `/schedule` - Manage schedules page

**Status Response Example:**
```json
{
  "state": "ON",
  "power": 125.5,
  "uptime": 1234567
}
```

---

## Error Responses

All endpoints return standardized error formats:

```json
{
  "error": "Error message here"
}
```

**HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request (missing parameters)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error

---

## Authentication (Coming Soon)

Future version will support:
- JWT Token authentication
- API Keys
- OAuth 2.0 integration

---

## Rate Limiting

Current implementation has no rate limiting. Future versions may implement:
- 100 requests per minute per IP
- Burst limit: 20 requests per second

---

## WebSocket Support (Future)

Planned endpoint for real-time updates:
```
ws://localhost:5000/ws
```

Subscription events:
- `device.state.changed`
- `power.threshold.reached`
- `schedule.triggered`

---

## SDK Examples

### JavaScript/Node.js

```javascript
// Toggle device
fetch('http://localhost:5000/api/devices/1/toggle', {
  method: 'POST'
})
.then(response => response.json())
.then(data => console.log(data));

// Create schedule
fetch('http://localhost:5000/api/schedules', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'Evening Lights',
    start_time: '19:00',
    end_time: '22:00',
    device_id: 1,
    daysOfWeek: 127
  })
});
```

### Python

```python
import requests

# Get all devices
response = requests.get('http://localhost:5000/api/devices')
devices = response.json()

# Toggle device
requests.post('http://localhost:5000/api/devices/1/toggle')

# Create schedule
schedule = {
    'name': 'Morning Brew',
    'start_time': '07:00',
    'end_time': '07:15',
    'device_id': 1,
    'daysOfWeek': 64
}
requests.post('http://localhost:5000/api/schedules', json=schedule)
```

### cURL

```bash
# List devices
curl http://localhost:5000/api/devices

# Toggle relay
curl -X POST http://localhost:5000/api/devices/1/toggle

# Create new schedule
curl -X POST http://localhost:5000/api/schedules \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","start_time":"12:00","end_time":"12:30","device_id":1}'
```

---

## Testing with Postman/Insomnia

Import collection URL: `https://gist.github.com/YOUR_GIST_ID`

Sample test scenarios:
1. ✅ Create device
2. ✅ List all devices  
3. ✅ Toggle device on/off
4. ✅ Check power history
5. ✅ Create weekly schedule
6. ✅ Verify daily statistics

---

## Changelog

**v1.0.0 (Current)**
- Basic REST API implemented
- Device CRUD operations
- Schedule management
- Power logging
- SQLite database backend

**Upcoming (v1.1.0)**
- User authentication
- WebSocket real-time updates
- MQTT integration
- Grafana dashboard support

---

For more information, visit: https://github.com/YOUR_USERNAME/smartplug-scheduler
