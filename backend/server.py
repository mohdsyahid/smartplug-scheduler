#!/usr/bin/env python3
"""
SmartPlug Scheduler - Backend Server
Author: Mohd Syahid
License: MIT

Features:
- REST API for device control
- Schedule management
- Power consumption logging
- WebSocket support (future)
"""

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import sqlite3
import json
import os
from datetime import datetime
import threading
import time

app = Flask(__name__)
CORS(app)

# Database configuration
DB_PATH = 'database.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database schema"""
    conn = get_db()
    
    # Devices table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mac_address TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Schedules table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER,
            name TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            daysOfWeek INTEGER DEFAULT 127,
            enabled INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (device_id) REFERENCES devices (id)
        )
    ''')
    
    # Power logs table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS power_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER,
            power_watts REAL NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (device_id) REFERENCES devices (id)
        )
    ''')
    
    # Relay history table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS relay_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER,
            state TEXT NOT NULL,
            changed_by TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (device_id) REFERENCES devices (id)
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/')
def dashboard():
    """Web dashboard interface"""
    html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartPlug Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #fff;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header { text-align: center; padding: 30px 0; }
        h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .subtitle { opacity: 0.9; font-size: 1.1rem; }
        
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }
        .stat-card { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 15px; padding: 25px; text-align: center; }
        .stat-card h3 { font-size: 0.9rem; opacity: 0.8; margin-bottom: 10px; }
        .stat-card .value { font-size: 2.5rem; font-weight: bold; color: #ffd700; }
        
        .main-content { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 30px; }
        @media (max-width: 768px) { .main-content { grid-template-columns: 1fr; } }
        
        .panel { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 15px; padding: 25px; }
        .panel h2 { margin-bottom: 20px; color: #ffd700; }
        
        .device-item { 
            background: rgba(255,255,255,0.15); 
            border-radius: 10px; 
            padding: 20px; 
            margin-bottom: 15px;
            transition: transform 0.3s;
        }
        .device-item:hover { transform: translateY(-5px); }
        .device-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .device-name { font-size: 1.2rem; font-weight: bold; }
        
        .toggle-btn {
            position: relative;
            width: 60px;
            height: 30px;
            background: #ff4757;
            border-radius: 30px;
            cursor: pointer;
            transition: background 0.3s;
        }
        .toggle-btn.active { background: #2ed573; }
        .toggle-btn::after {
            content: '';
            position: absolute;
            top: 3px;
            left: 3px;
            width: 24px;
            height: 24px;
            background: white;
            border-radius: 50%;
            transition: transform 0.3s;
        }
        .toggle-btn.active::after { transform: translateX(30px); }
        
        button.action-btn {
            background: #3742fa;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            margin: 5px;
            transition: all 0.3s;
        }
        button.action-btn:hover { background: #5352ed; transform: translateY(-2px); }
        
        input[type="text"], input[type="time"] {
            padding: 12px;
            border-radius: 8px;
            border: none;
            width: 100%;
            margin-bottom: 10px;
            font-size: 14px;
        }
        
        .power-chart {
            width: 100%;
            height: 200px;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎯 SmartPlug Scheduler</h1>
            <p class="subtitle">Monitor & Control Your Smart Home Devices</p>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Devices</h3>
                <div class="value" id="deviceCount">-</div>
            </div>
            <div class="stat-card">
                <h3>Active Now</h3>
                <div class="value" id="activeDevices">-</div>
            </div>
            <div class="stat-card">
                <h3>Today's Usage</h3>
                <div class="value" id="dailyUsage">-</div>
            </div>
        </div>
        
        <div class="main-content">
            <div class="panel">
                <h2>🔌 Connected Devices</h2>
                <div id="devicesList"></div>
            </div>
            
            <div class="panel">
                <h2>⏰ Create Schedule</h2>
                <form id="scheduleForm">
                    <input type="text" id="scheduleName" placeholder="Schedule Name" required>
                    <input type="time" id="startTime" required>
                    <input type="time" id="endTime" required>
                    <select id="daysOfWeek" style="padding: 12px; border-radius: 8px; width: 100%;">
                        <option value="127">Every Day</option>
                        <option value="64" selected>Mon-Fri</option>
                        <option value="96">Weekends</option>
                        <option value="127">Custom Days</option>
                    </select>
                    <button type="submit" class="action-btn" style="width: 100%;">Create Schedule</button>
                </form>
                <div id="schedulesList" style="margin-top: 20px;"></div>
            </div>
        </div>
        
        <div class="panel" style="margin-top: 30px;">
            <h2>📊 Power Consumption History</h2>
            <canvas id="powerChart" class="power-chart"></canvas>
        </div>
    </div>
    
    <script>
        const API_BASE = '/api';
        
        async function loadDashboard() {
            try {
                const devicesRes = await fetch(`${API_BASE}/devices`);
                const devices = await devicesRes.json();
                
                document.getElementById('deviceCount').textContent = devices.length;
                const activeCount = devices.filter(d => d.state === 'on').length;
                document.getElementById('activeDevices').textContent = activeCount;
                
                // Render devices
                const devicesList = document.getElementById('devicesList');
                devicesList.innerHTML = devices.map(device => `
                    <div class="device-item">
                        <div class="device-header">
                            <span class="device-name">${device.name}</span>
                            <div class="toggle-btn ${device.state === 'on' ? 'active' : ''}" 
                                 onclick="toggleDevice(${device.id})"></div>
                        </div>
                        <div style="display: flex; gap: 10px;">
                            <button class="action-btn" onclick="scheduleDevice(${device.id})">Schedule</button>
                            <button class="action-btn" onclick="showHistory(${device.id})">History</button>
                        </div>
                    </div>
                `).join('');
            } catch(error) {
                console.error('Error loading dashboard:', error);
            }
        }
        
        async function toggleDevice(deviceId) {
            try {
                await fetch(`${API_BASE}/devices/${deviceId}/toggle`, { method: 'POST' });
                loadDashboard();
            } catch(error) {
                console.error('Error toggling device:', error);
            }
        }
        
        async function showHistory(deviceId) {
            try {
                const res = await fetch(`${API_BASE}/devices/${deviceId}/history?limit=50`);
                const history = await res.json();
                
                const lastHour = history.slice(-5);
                const avgPower = lastHour.reduce((sum, r) => sum + r.power_watts, 0) / lastHour.length;
                
                alert(`Last 5 readings:\\n\\n${lastHour.map(r => 
                    `${new Date(r.timestamp).toLocaleTimeString()}: ${r.power_watts.toFixed(1)}W`
                ).join('\\n')}\\n\\nAverage: ${avgPower.toFixed(1)}W`);
            } catch(error) {
                console.error('Error loading history:', error);
            }
        }
        
        document.getElementById('scheduleForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const schedule = {
                name: document.getElementById('scheduleName').value,
                start_time: document.getElementById('startTime').value,
                end_time: document.getElementById('endTime').value,
                daysOfWeek: parseInt(document.getElementById('daysOfWeek').value),
                device_id: 1 // Default device for now
            };
            
            try {
                await fetch(`${API_BASE}/schedules`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(schedule)
                });
                
                alert('Schedule created successfully!');
                e.target.reset();
            } catch(error) {
                console.error('Error creating schedule:', error);
            }
        });
        
        // Initial load
        loadDashboard();
        
        // Refresh every 5 seconds
        setInterval(loadDashboard, 5000);
    </script>
</body>
</html>
'''
    return render_template_string(html)

# API Routes

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Get all devices"""
    conn = get_db()
    devices = conn.execute('SELECT * FROM devices ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(device) for device in devices])

@app.route('/api/devices/<int:device_id>', methods=['GET'])
def get_device(device_id):
    """Get single device by ID"""
    conn = get_db()
    device = conn.execute('SELECT * FROM devices WHERE id = ?', (device_id,)).fetchone()
    conn.close()
    if device:
        return jsonify(dict(device))
    return jsonify({'error': 'Device not found'}), 404

@app.route('/api/devices', methods=['POST'])
def create_device():
    """Create new device"""
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Device name is required'}), 400
    
    conn = get_db()
    cursor = conn.execute(
        'INSERT INTO devices (name, mac_address) VALUES (?, ?)',
        (data['name'], data.get('mac_address'))
    )
    device_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'id': device_id,
        'name': data['name'],
        'mac_address': data.get('mac_address'),
        'state': 'off'
    }), 201

@app.route('/api/devices/<int:device_id>/toggle', methods=['POST'])
def toggle_device(device_id):
    """Toggle device state"""
    conn = get_db()
    
    # Check if device exists
    device = conn.execute('SELECT * FROM devices WHERE id = ?', (device_id,)).fetchone()
    if not device:
        conn.close()
        return jsonify({'error': 'Device not found'}), 404
    
    # Toggle state
    new_state = 'on' if device['state'] == 'off' else 'off'
    
    conn.execute(
        'UPDATE devices SET state = ? WHERE id = ?',
        (new_state, device_id)
    )
    
    # Log to history
    conn.execute(
        'INSERT INTO relay_history (device_id, state, changed_by) VALUES (?, ?, ?)',
        (device_id, new_state, 'manual')
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'id': device_id,
        'name': device['name'],
        'state': new_state
    })

@app.route('/api/devices/<int:device_id>/history', methods=['GET'])
def get_device_history(device_id):
    """Get power consumption history"""
    limit = request.args.get('limit', 50, type=int)
    
    conn = get_db()
    history = conn.execute(
        '''SELECT * FROM power_logs 
           WHERE device_id = ? 
           ORDER BY timestamp DESC 
           LIMIT ?''',
        (device_id, limit)
    ).fetchall()
    conn.close()
    
    return jsonify([dict(entry) for entry in history])

@app.route('/api/schedules', methods=['GET'])
def get_schedules():
    """Get all schedules"""
    conn = get_db()
    schedules = conn.execute('SELECT * FROM schedules ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(schedule) for schedule in schedules])

@app.route('/api/schedules', methods=['POST'])
def create_schedule():
    """Create new schedule"""
    data = request.get_json()
    
    required_fields = ['name', 'start_time', 'end_time', 'device_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = get_db()
    cursor = conn.execute(
        '''INSERT INTO schedules (name, start_time, end_time, device_id, daysOfWeek) 
           VALUES (?, ?, ?, ?, ?)''',
        (data['name'], data['start_time'], data['end_time'], 
         data['device_id'], data.get('daysOfWeek', 127))
    )
    schedule_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'id': schedule_id, 'message': 'Schedule created'}), 201

@app.route('/api/stats/daily', methods=['GET'])
def get_daily_stats():
    """Get daily statistics"""
    today = datetime.now().date().isoformat()
    
    conn = get_db()
    
    # Get total energy consumed today
    usage = conn.execute(
        '''SELECT SUM(power_watts) as total, AVG(power_watts) as average, COUNT(*) as count
           FROM power_logs 
           WHERE DATE(timestamp) = ?''',
        (today,)
    ).fetchone()
    
    conn.close()
    
    return jsonify({
        'date': today,
        'total_watts': round(usage['total'] or 0, 2),
        'average_watts': round(usage['average'] or 0, 2),
        'readings_count': usage['count']
    })

if __name__ == '__main__':
    print("Initializing SmartPlug Scheduler Backend...")
    init_db()
    print("Database initialized!")
    print("Starting server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
