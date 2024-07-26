# ESP8266 Temperature Monitoring System

## Overview

This project involves using an ESP8266 microcontroller to collect temperature data from a DS18B20 sensor and send this data to a FastAPI server. The ESP8266 connects to a Wi-Fi network and periodically sends temperature readings along with timestamps to a specified endpoint on the server.

## Features

- **ESP8266 Microcontroller**: Handles Wi-Fi connectivity and communication.
- **DS18B20 Temperature Sensor**: Measures the temperature.
- **FastAPI Server**: Receives and stores temperature data.
- **Data Transmission**: Uses HTTP POST requests to send data to the server.
- **Data Retrieval**: Supports data retrieval via HTTP GET requests.

## Hardware Requirements

- ESP8266 microcontroller (e.g., ESP-01, NodeMCU, Wemos D1 Mini)
- DS18B20 Temperature Sensor
- 4.7kΩ Resistor (for DS18B20)
- Breadboard and Jumper Wires

## Software Requirements

- Arduino IDE
- FastAPI
- Python
- SQLite (optional, for database storage)

## Setup Instructions

### 1. Hardware Setup

1. **Connect the DS18B20 Sensor to the ESP8266:**
   - **VCC** to 3.3V
   - **GND** to GND
   - **DATA** to GPIO 2 (D4 on NodeMCU)

2. **Add a 4.7kΩ Pull-up Resistor** between the DATA pin and VCC.

### 2. Software Setup

#### ESP8266 Firmware

1. Open the Arduino IDE.
2. Install the ESP8266 board support package via the Board Manager.
3. Install the following libraries:
   - `ESP8266WiFi`
   - `ESP8266HTTPClient`
   - `OneWire`
   - `DallasTemperature`
4. Load the provided code onto the ESP8266:

   ```cpp
   #include <ESP8266WiFi.h>
   #include <ESP8266HTTPClient.h>
   #include <OneWire.h>
   #include <DallasTemperature.h>
   #include <time.h>

   const char* ssid = "your_wifi_ssid";
   const char* password = "your_wifi_password";
   const char* serverName = "http://10.1.89.50:8001/collect-data/";

   #define ONE_WIRE_BUS 2

   OneWire oneWire(ONE_WIRE_BUS);
   DallasTemperature sensors(&oneWire);

   void setup() {
     Serial.begin(115200);
     WiFi.begin(ssid, password);
     while (WiFi.status() != WL_CONNECTED) {
       delay(1000);
       Serial.print(".");
     }
     Serial.println("Connected!");
     sensors.begin();
     configTime(0, 0, "pool.ntp.org", "time.nist.gov");
   }

   void loop() {
     delay(2000);
     sensors.requestTemperatures();
     float temperature = sensors.getTempCByIndex(0);

     if (temperature == DEVICE_DISCONNECTED_C) {
       Serial.println("Failed to read from DS18B20 sensor!");
       return;
     }

     time_t now = time(nullptr);
     struct tm* timeinfo = localtime(&now);
     char timestamp[80];
     strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%S%z", timeinfo);

     String httpRequestData = "{\"temperature\":" + String(temperature) + ",\"timestamp\":\"" + String(timestamp) + "\"}";
     Serial.print("Temperature: ");
     Serial.print(temperature);
     Serial.print(" °C, Timestamp: ");
     Serial.println(timestamp);

     if (WiFi.status() == WL_CONNECTED) {
       HTTPClient http;
       http.begin(serverName);
       http.addHeader("Content-Type", "application/json");
       int httpResponseCode = http.POST(httpRequestData);

       if (httpResponseCode > 0) {
         String response = http.getString();
         Serial.println(httpResponseCode);
         Serial.println(response);
       } else {
         Serial.print("Error on sending POST: ");
         Serial.println(httpResponseCode);
       }
       http.end();
     } else {
       Serial.println("WiFi Disconnected");
     }
   }
```

## Step 1 : 
```ardunio
   const char* ssid = "your_wifi_ssid";
   const char* password = "your_wifi_password";
   const char* serverName = "http://10.1.89.50:8001/collect-data/";

```
add wifi details 
ssid is the wifi name 
password is password 
change the ip address of your laptop 

use ipconfig to know the ipaddress 
```bash
ipconfig
```

```bash
Wireless LAN adapter Wi-Fi:

   Connection-specific DNS Suffix  . : srmap.univ
   Link-local IPv6 Address . . . . . : fe80::c971:c433:6bbc:cb76%14
   IPv4 Address. . . . . . . . . . . : 10.1.89.50
   Subnet Mask . . . . . . . . . . . : 255.255.255.0
   Default Gateway . . . . . . . . . : 10.1.89.254

Ethernet adapter Bluetooth Network Connection:

   Media State . . . . . . . . . . . : Media disconnected
   Connection-specific DNS Suffix  . :
PS C:\Users\pandu>

```
pick the IPV4 Address
"http://10.1.89.50:8080/collect-data/";

## step 2:

Adruino modules 

```bash
https://www.instructables.com/Steps-to-Setup-Arduino-IDE-for-NODEMCU-ESP8266-WiF/
```

Go to Board Manager and type ESP8266 
install it 

check the port number from device manager 
after run the python file 


