# ESP32 Documentation for ArchaeoScan

## 📡 Server URLs

### Railway Backend URL
```
https://web-production-263d0.up.railway.app
```

### API Endpoints
```
POST https://web-production-263d0.up.railway.app/api/esp32/data
GET  https://web-production-263d0.up.railway.app/api/esp32/status
WebSocket: wss://web-production-263d0.up.railway.app/ws
ESP32 WebSocket: wss://web-production-263d0.up.railway.app/api/esp32/ws
```

## 📤 JSON Format for ESP32 → Server

### Required Data Structure
```json
{
  "lat": 43.2345,
  "lng": 51.3456,
  "depth": 12.4,
  "mag": 34.1,
  "spectrum": [12.5, 15.2, 18.7, 22.1, 25.3, 28.9, 32.4, 35.8],
  "timestamp": 1707043200,
  "device_id": "ESP32_001"
}
```

### Field Descriptions
- `lat`: Latitude (float) - Широта
- `lng`: Longitude (float) - Долгота  
- `depth`: Depth in meters (float) - Глубина в метрах
- `mag`: Magnetic field strength (float) - Сила магнитного поля
- `spectrum`: Spectrometer data array (float[]) - Данные спектрометра
- `timestamp`: Unix timestamp (int) - Время в Unix формате
- `device_id`: Optional device identifier (string) - ID устройства

## 🔄 ESP32 Code Example (Arduino)

### HTTP POST Method
```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <GPS.h>
#include <Spectrometer.h>
#include <Magnetometer.h>

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverUrl = "https://web-production-263d0.up.railway.app/api/esp32/data";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  
  initializeSensors();
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    sendSensorData();
  }
  delay(5000); // Send every 5 seconds
}

void sendSensorData() {
  // Read sensor data
  float lat = GPS.getLatitude();
  float lng = GPS.getLongitude();
  float depth = getDepth();
  float mag = Magnetometer.read();
  float spectrum[8];
  Spectrometer.read(spectrum, 8);
  
  // Create JSON document
  StaticJsonDocument<200> doc;
  doc["lat"] = lat;
  doc["lng"] = lng;
  doc["depth"] = depth;
  doc["mag"] = mag;
  
  JsonArray spectrumArray = doc.createNestedArray("spectrum");
  for (int i = 0; i < 8; i++) {
    spectrumArray.add(spectrum[i]);
  }
  
  doc["timestamp"] = millis() / 1000;
  doc["device_id"] = "ESP32_001";
  
  // Serialize to string
  String jsonString;
  serializeJson(doc, jsonString);
  
  // Send HTTP POST
  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");
  
  int httpResponseCode = http.POST(jsonString);
  
  if (httpResponseCode == 200) {
    Serial.println("Data sent successfully");
    String response = http.getString();
    Serial.println(response);
  } else {
    Serial.print("Error sending data: ");
    Serial.println(httpResponseCode);
  }
  
  http.end();
}
```

### WebSocket Method (Real-time)
```cpp
#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>

const char* websocketUrl = "wss://web-production-263d0.up.railway.app/api/esp32/ws";
WebSocketsClient webSocket;

void setup() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
  }
  
  webSocket.begin(websocketUrl);
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000);
}

void loop() {
  webSocket.loop();
  
  static unsigned long lastSend = 0;
  if (millis() - lastSend > 5000) { // Send every 5 seconds
    sendSensorDataWebSocket();
    lastSend = millis();
  }
}

void sendSensorDataWebSocket() {
  // Same sensor reading as HTTP method
  StaticJsonDocument<200> doc;
  doc["lat"] = GPS.getLatitude();
  doc["lng"] = GPS.getLongitude();
  doc["depth"] = getDepth();
  doc["mag"] = Magnetometer.read();
  
  JsonArray spectrumArray = doc.createNestedArray("spectrum");
  float spectrum[8];
  Spectrometer.read(spectrum, 8);
  for (int i = 0; i < 8; i++) {
    spectrumArray.add(spectrum[i]);
  }
  
  doc["timestamp"] = millis() / 1000;
  doc["device_id"] = "ESP32_001";
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  webSocket.sendTXT(jsonString);
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch(type) {
    case WStype_DISCONNECTED:
      Serial.println("Disconnected from WebSocket");
      break;
    case WStype_CONNECTED:
      Serial.println("Connected to WebSocket");
      break;
    case WStype_TEXT:
      Serial.printf("Received: %s\n", payload);
      break;
  }
}
```

## 🔧 Server Response Format

### Success Response
```json
{
  "status": "success",
  "message": "Data received successfully",
  "timestamp": 1707043200
}
```

### Error Response
```json
{
  "status": "error",
  "message": "Failed to process data",
  "timestamp": 1707043200
}
```

## 📊 Status Check

### GET /api/esp32/status Response
```json
{
  "connected": true,
  "last_seen": 1707043200,
  "seconds_since_last": 5,
  "message": "Online"
}
```

## 🎯 Important Notes

1. **Timestamp**: Use Unix timestamp (seconds since 1970)
2. **Coordinates**: Use decimal degrees format
3. **Spectrum**: Send as array of floats (typically 8-16 values)
4. **Depth**: Positive value (meters below surface)
5. **Magnetic**: Field strength in microtesla (μT)
6. **Rate**: Send data every 1-5 seconds for real-time tracking

## 🚀 Testing

You can test the API with curl:
```bash
curl -X POST https://web-production-263d0.up.railway.app/api/esp32/data \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 43.2345,
    "lng": 51.3456,
    "depth": 12.4,
    "mag": 34.1,
    "spectrum": [12.5, 15.2, 18.7, 22.1, 25.3, 28.9, 32.4, 35.8],
    "timestamp": 1707043200,
    "device_id": "TEST_001"
  }'
```

## 📡 Network Requirements

- **WiFi**: 2.4GHz or 5GHz
- **Internet**: Required for Railway backend
- **Protocol**: HTTPS/WSS (secure connections)
- **Data Rate**: ~1KB per transmission
- **Frequency**: 1-5 seconds recommended
