#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>

#define SERIAL_BAUD 115200

const char* ssid = "TelstraE8752E";  // Replace with your network credentials
const char* password = "j5cph5asws7wcfkm";

ESP8266WebServer server(80);

void setup() {
  Serial.begin(SERIAL_BAUD);
  WiFi.begin(ssid, password);
  
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
  
  server.on("/", handleRoot);
  server.on("/update_pwm", handlePWMUpdate);

  // Directional commands
  server.on("/FORWARD", []() {
    Serial.println("FORWARD");
    server.send(200, "text/plain", "Moving Forward");
  });
  server.on("/BACKWARD", []() {
    Serial.println("BACKWARD");
    server.send(200, "text/plain", "Moving Backward");
  });
  server.on("/LEFT", []() {
    Serial.println("LEFT");
    server.send(200, "text/plain", "Turning Left");
  });
  server.on("/RIGHT", []() {
    Serial.println("RIGHT");
    server.send(200, "text/plain", "Turning Right");
  });

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

  server.begin();
}

void handlePWMUpdate() {
  String motor = server.arg("motor");
  String value = server.arg("value");
  Serial.print("M");
  Serial.print(motor);
  Serial.print("_PWM_");
  Serial.println(value);
  server.send(200, "text/plain", "PWM Updated");
}

void handleRoot() {
  String html = "<html><body>"
                "<h1>Motor Control</h1>"
                "<div style='text-align: center;'>"
                "<button onclick=\"sendCommand('FORWARD')\" style='width: 100px; height: 100px;'>Up</button><br>"
                "<button onclick=\"sendCommand('LEFT')\" style='width: 100px; height: 100px;'>Left</button>"
                "<button onclick=\"sendCommand('AI')\" style='width: 100px; height: 100px; background-color: blue; color: white;'>AI</button>"
                "<button onclick=\"sendCommand('RIGHT')\" style='width: 100px; height: 100px;'>Right</button><br>"
                "<button onclick=\"sendCommand('BACKWARD')\" style='width: 100px; height: 100px;'>Down</button>"
                "</div>"
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
                "</script>"
                "</body></html>";
  server.send(200, "text/html", html);
}
void loop() {
  server.handleClient();
}

// ... (rest of your existing code)
