#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>

#define SERIAL_BAUD 115200

// Replace with your network credentials
const char* ssid = "your router";
const char* password = "wifi password";

// Create an instance of the web server
// Specify the port to listen on
ESP8266WebServer server(80);

void setup() {
  // Start the serial communication
  Serial.begin(115200);
    
  WiFi.begin(ssid, password);
  
    // Define a route to handle PWM updates
  server.on("/update_pwm", handlePWMUpdate);
  
  unsigned long startAttemptTime = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < 15000) {
    delay(500);
    Serial.print(".");
  }
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Failed to connect to WiFi. Please check your credentials");
  } else {
    Serial.print("Connected to ");
    Serial.print(ssid);
    Serial.print(", IP address: ");
    Serial.println(WiFi.localIP());
  }
  
  // Print the IP address
  Serial.println(WiFi.localIP());
  
  // Define web server routes
  server.on("/", handleRoot);
  server.on("/M3_FORWARD", []() {
    Serial.println("M3_FORWARD");
    server.send(200, "text/plain", "Back Motor Forward");
  });
  server.on("/M3_BACKWARD", []() {
    Serial.println("M3_BACKWARD");
    server.send(200, "text/plain", "Back Motor Backward");
  });
  server.on("/M3_STOP", []() {
    Serial.println("M3_STOP");
    server.send(200, "text/plain", "Back Motor Stop");
  });
  server.on("/M4_FORWARD", []() {
    Serial.println("M4_FORWARD");
    server.send(200, "text/plain", "Back Motor Forward");
  });
  server.on("/M4_BACKWARD", []() {
    Serial.println("M4_BACKWARD");
    server.send(200, "text/plain", "Back Motor Backward");
  });
  server.on("/M4_STOP", []() {
    Serial.println("M4_STOP");
    server.send(200, "text/plain", "Back Motor Stop");
  });
  
  // Start the server
  server.begin();
}


void handlePWMUpdate() {
  String motor = server.arg("motor");
  String value = server.arg("value");

  Serial.print("M"); // Motor identifier
  Serial.print(motor);
  Serial.print("_PWM_");
  Serial.println(value);

  server.send(200, "text/plain", "PWM Updated");
}

void loop() {
  // Handle client requests
  server.handleClient();
}

void handleRoot() {
  String html = "<html><body>"
              "<h1>Motor Control</h1>"
              "<p>Motor 1: <input type='range' min='0' max='255' onchange='updatePWM(1, this.value)' /></p>"
              "<p>Motor 2: <input type='range' min='0' max='255' onchange='updatePWM(2, this.value)' /></p>"
              "<p><button onclick=\"sendCommand('M3_FORWARD')\">Back Motor Forward</button></p>"
              "<p><button onclick=\"sendCommand('M3_BACKWARD')\">Back Motor Backward</button></p>"
              "<p><button onclick=\"sendCommand('M3_STOP')\">Back Motor Stop</button></p>"
              "<p><button onclick=\"sendCommand('M4_FORWARD')\">Back Motor Backward</button></p>"
              "<p><button onclick=\"sendCommand('M4_BACKWARD')\">Back Motor Forward</button></p>"
              "<p><button onclick=\"sendCommand('M4_STOP')\">Back Motor Stop</button></p>"
              "<script>"
              "function sendCommand(command) {"
              "  var xhttp = new XMLHttpRequest();"
              "  xhttp.onreadystatechange = function() {"
              "    if (this.readyState == 4 && this.status == 200) {"
              "      console.log('Command sent: ' + command);"
              "    }"
              "  };"
              "  xhttp.open('GET', '/' + command, true);"
              "  xhttp.send();"
              "}"
              "function updatePWM(motor, value) {"
              "  var xhttp = new XMLHttpRequest();"
              "  xhttp.open('GET', '/update_pwm?motor=' + motor + '&value=' + value, true);"
              "  xhttp.send();"
              "}"
              "</script>"
              "</body></html>";
  server.send(200, "text/html", html);
}
