#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <time.h>

// Replace these with your network credentials
const char* ssid = "pandusai 11i";

const char* password = "8688670712";

// Replace with your server's URL
const char* serverName = "http://10.1.177.171:8080/collect-data/";

// Data wire is plugged into GPIO 2 on the ESP8266
#define ONE_WIRE_BUS 2

// Setup a oneWire instance to communicate with any OneWire devices
OneWire oneWire(ONE_WIRE_BUS);

// Pass our oneWire reference to Dallas Temperature sensor 
DallasTemperature sensors(&oneWire);

// Create a WiFiClient object
WiFiClient wifiClient;

void setup() {
  Serial.begin(115200);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println(" Connected!");

  // Initialize DS18B20 sensor
  sensors.begin();

  // Initialize time
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
}

void loop() {
  // Wait a few seconds between measurements
  delay(2000);

  // Request temperature from sensor
  sensors.requestTemperatures();
  float temperature = sensors.getTempCByIndex(0);

  // Check if the read is valid
  if (temperature == DEVICE_DISCONNECTED_C) {
    Serial.println("Failed to read from DS18B20 sensor!");
    return;
  }

  // Get current timestamp
  time_t now = time(nullptr);
  struct tm* timeinfo = localtime(&now);
  char timestamp[80];
  strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%S%z", timeinfo);

  // Prepare JSON payload
  String httpRequestData = "{\"temperature\":" + String(temperature) + ",\"timestamp\":\"" + String(timestamp) + "\"}";

  // Print temperature and timestamp to Serial Monitor
  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.print(" °C, Timestamp: ");
  Serial.println(timestamp);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    // Your server URL
    http.begin(wifiClient, serverName);  // Updated to use WiFiClient

    // Specify content-type header
    http.addHeader("Content-Type", "application/json");

    // Send HTTP POST request
    int httpResponseCode = http.POST(httpRequestData);

    // Print response
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println(httpResponseCode);
      Serial.println(response);
    } else {
      Serial.print("Error on sending POST: ");
      Serial.println(httpResponseCode);
    }

    // Free resources
    http.end();
  } else {
    Serial.println("WiFi Disconnected");
  }
}
