#define SERIAL_BAUD 115200

// Pins for PWM-controlled motors (front)
const int motorFRPinPWM = 5; // Front Right motor PWM pin
const int motorFLPinPWM = 6; // Front Left motor PWM pin

// Pins for L298N-controlled motors (back)
const int motorBRPin1 = 7; // Back Right motor Pin 1
const int motorBRPin2 = 8; // Back Right motor Pin 2
const int motorBLPin1 = 9; // Back Left motor Pin 1
const int motorBLPin2 = 10; // Back Left motor Pin 2

String command; // To store the incoming serial command

void setup() {
  Serial.begin(SERIAL_BAUD);

  // Initialize front motor pins (PWM)
  pinMode(motorFRPinPWM, OUTPUT);
  pinMode(motorFLPinPWM, OUTPUT);

  // Initialize back motor pins (L298N)
  pinMode(motorBRPin1, OUTPUT);
  pinMode(motorBRPin2, OUTPUT);
  pinMode(motorBLPin1, OUTPUT);
  pinMode(motorBLPin2, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    command = Serial.readStringUntil('\n');
    command.trim(); // Remove any whitespace or newline characters
    Serial.println(command); // Echo the command to Serial for debugging

    // Handle PWM commands
    if (command.startsWith("M1_PWM_")) {
      int pwmValue = command.substring(7).toInt();
      analogWrite(motorFRPinPWM, pwmValue);
    } else if (command.startsWith("M2_PWM_")) {
      int pwmValue = command.substring(7).toInt();
      analogWrite(motorFLPinPWM, pwmValue);
    }

    // Handle L298N motor commands
    else if (command == "M3_FORWARD") {
      digitalWrite(motorBRPin1, HIGH);
      digitalWrite(motorBRPin2, LOW);
    } else if (command == "M3_BACKWARD") {
      digitalWrite(motorBRPin1, LOW);
      digitalWrite(motorBRPin2, HIGH);
    } else if (command == "M3_STOP") {
      digitalWrite(motorBRPin1, LOW);
      digitalWrite(motorBRPin2, LOW);
    } else if (command == "M4_FORWARD") {
      digitalWrite(motorBLPin1, HIGH);
      digitalWrite(motorBLPin2, LOW);
    } else if (command == "M4_BACKWARD") {
      digitalWrite(motorBLPin1, LOW);
      digitalWrite(motorBLPin2, HIGH);
    } else if (command == "M4_STOP") {
      digitalWrite(motorBLPin1, LOW);
      digitalWrite(motorBLPin2, LOW);
    }
    // Clear the command string to get ready for the next command
    command = "";
  }
}