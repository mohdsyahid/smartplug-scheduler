package com.smartplug.scheduler

import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import kotlinx.coroutines.*
import okhttp3.*
import org.json.JSONObject
import java.io.IOException
import kotlin.concurrent.thread

class MainActivity : AppCompatActivity() {
    
    private lateinit var toggleBtn: Button
    private lateinit var statusView: TextView
    private lateinit var powerView: TextView
    private lateinit var devicesList: ListView
    private lateinit var addScheduleBtn: Button
    
    private val client = OkHttpClient()
    private var deviceIp = "192.168.1.100" // Change this to ESP32 IP or get via config
    private var apiKey = ""
    
    companion object {
        private const val API_TIMEOUT = 5000 // 5 seconds timeout
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        initViews()
        loadSettings()
        startStatusPolling()
    }
    
    private fun initViews() {
        toggleBtn = findViewById(R.id.toggleBtn)
        statusView = findViewById(R.id.statusView)
        powerView = findViewById(R.id.powerView)
        devicesList = findViewById(R.id.devicesList)
        addScheduleBtn = findViewById(R.id.addScheduleBtn)
        
        toggleBtn.setOnClickListener {
            toggleCurrentDevice()
        }
        
        addScheduleBtn.setOnClickListener {
            showAddScheduleDialog()
        }
        
        // Configure device list adapter
        devicesList.onItemClickListener = AdapterView.OnItemClickListener { _, _, position, _ ->
            selectDevice(position)
        }
    }
    
    private fun loadSettings() {
        val prefs = getSharedPreferences("smartplug_prefs", MODE_PRIVATE)
        deviceIp = prefs.getString("device_ip", "192.168.1.100") ?: "192.168.1.100"
        apiKey = prefs.getString("api_key", "") ?: ""
        
        updateApiUrl()
    }
    
    private fun updateApiUrl() {
        // Update UI with current settings
        Toast.makeText(this, "Using API: http://$deviceIp", Toast.LENGTH_SHORT).show()
    }
    
    private fun startStatusPolling() {
        thread {
            while (true) {
                fetchStatus()
                try {
                    Thread.sleep(5000) // Poll every 5 seconds
                } catch (e: InterruptedException) {
                    break
                }
            }
        }
    }
    
    private fun fetchStatus() {
        val request = Request.Builder()
            .url("http://$deviceIp/status")
            .timeout(API_TIMEOUT.toLong(), java.util.concurrent.TimeUnit.MILLISECONDS)
            .build()
        
        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                runOnUiThread {
                    Toast.makeText(
                        this@MainActivity, 
                        "Connection failed: $deviceIp", 
                        Toast.LENGTH_SHORT
                    ).show()
                }
            }
            
            override fun onResponse(call: Call, response: Response) {
                response.body?.string()?.let { responseBody ->
                    runOnUiThread {
                        try {
                            val json = JSONObject(responseBody)
                            val state = json.getString("state")
                            val power = json.getDouble("power")
                            
                            statusView.text = "State: $state"
                            statusView.setTextColor(
                                if (state == "ON") 
                                    getColor(R.color.green) 
                                else 
                                    getColor(R.color.red)
                            )
                            
                            powerView.text = String.format("Power: %.1f W", power)
                            
                        } catch (e: Exception) {
                            e.printStackTrace()
                        }
                    }
                }
            }
        })
    }
    
    private fun toggleCurrentDevice() {
        // For direct ESP32 control, skip backend
        val request = Request.Builder()
            .url("http://$deviceIp/toggle")
            .post(null)
            .timeout(API_TIMEOUT.toLong(), java.util.concurrent.TimeUnit.MILLISECONDS)
            .build()
        
        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                runOnUiThread {
                    Toast.makeText(this@MainActivity, "Toggle failed!", Toast.LENGTH_SHORT).show()
                }
            }
            
            override fun onResponse(call: Call, response: Response) {
                runOnUiThread {
                    Toast.makeText(this@MainActivity, "Device toggled!", Toast.LENGTH_SHORT).show()
                }
            }
        })
    }
    
    private fun selectDevice(position: Int) {
        // Implement device selection logic here
        Toast.makeText(this, "Selected device #$position", Toast.LENGTH_SHORT).show()
    }
    
    private fun showAddScheduleDialog() {
        val dialog = AlertDialog.Builder(this).apply {
            setTitle("Add Schedule")
            
            val inputName = EditText(this@MainActivity).apply {
                hint = "Schedule Name"
            }
            
            val inputTime = TimePicker(this@MainActivity).apply {
                hour = 19
                minute = 0
            }
            
            setView(arrayOf(inputName, inputTime))
            
            setPositiveButton("Add") { _, _ ->
                saveSchedule(inputName.text.toString(), inputTime)
            }
            
            setNegativeButton("Cancel", null)
        }.create()
        
        dialog.show()
    }
    
    private fun saveSchedule(name: String, timePicker: TimePicker) {
        val scheduleData = """
        {
            "name": "$name",
            "start_time": "${timePicker.hour}:00",
            "end_time": "${timePicker.hour + 1}:00",
            "device_id": 1,
            "daysOfWeek": 127
        }
        """.trimIndent()
        
        val request = Request.Builder()
            .url("http://localhost:5000/api/schedules")
            .addHeader("Content-Type", "application/json")
            .post(scheduleData.toRequestBody())
            .build()
        
        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                runOnUiThread {
                    Toast.makeText(this@MainActivity, "Failed to save schedule", Toast.LENGTH_SHORT).show()
                }
            }
            
            override fun onResponse(call: Call, response: Response) {
                runOnUiThread {
                    Toast.makeText(this@MainActivity, "Schedule saved!", Toast.LENGTH_SHORT).show()
                }
            }
        })
    }
}
