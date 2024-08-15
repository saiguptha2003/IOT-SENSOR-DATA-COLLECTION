#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <time.h>

const char* ssid = "s********";
const char* password = "I*********";
const char* serverName = "http://10.1.65.44:8081/collect-sensor-data/";

#define ONE_WIRE_BUS 2
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
WiFiClient wifiClient;

#define DO_SENSOR_PIN A0
#define VREF    5000
#define ADC_RES 1024
#define MAX_DO_CONCENTRATION 20.0
#define MAX_VOLTAGE 5000

unsigned long previousMillis = 0;
const long interval = 60000;

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println(" Connected!");

  sensors.begin();
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    sensors.requestTemperatures();
    float temperature = sensors.getTempCByIndex(0);

    if (temperature == DEVICE_DISCONNECTED_C) {
      Serial.println("Failed to read from DS18B20 sensor!");
      return;
    }

    uint32_t raw = analogRead(DO_SENSOR_PIN);
    uint32_t voltage = (raw * VREF) / ADC_RES;
    float do_concentration = (voltage / (float)MAX_VOLTAGE) * MAX_DO_CONCENTRATION;

    String httpRequestData = "{\"temperature\":" + String(temperature) + ",\"do_concentration\":" + String(do_concentration) + "}";

    Serial.print("Sending data: ");
    Serial.println(httpRequestData);

    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(wifiClient, serverName);
      http.addHeader("Content-Type", "application/json");

      int httpResponseCode = http.POST(httpRequestData);

      Serial.print("HTTP Response Code: ");
      Serial.println(httpResponseCode);

      if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.print("Response: ");
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
}