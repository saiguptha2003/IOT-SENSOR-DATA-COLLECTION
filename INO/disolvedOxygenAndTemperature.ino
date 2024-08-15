#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <time.h>

const char* ssid = "pandusai 11i";
const char* password = "8688670712";
const char* serverName = "http://54.175.138.36:8080/collect-data/";

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
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
  }
  sensors.begin();
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    sensors.requestTemperatures();
    float temperature = sensors.getTempCByIndex(0);

    uint32_t raw = analogRead(DO_SENSOR_PIN);
    uint32_t voltage = (raw * VREF) / ADC_RES;
    float do_concentration = (voltage / (float)MAX_VOLTAGE) * MAX_DO_CONCENTRATION;

    String httpRequestData = "{\"temperature\":" + String(temperature) + ",\"do_concentration\":" + String(do_concentration) + "}";

    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(wifiClient, serverName);
      http.addHeader("Content-Type", "application/json");
      http.POST(httpRequestData);
      http.end();
    }
  }
}
