
import RPi.GPIO as GPIO

# Set up GPIO pins for motors
motor1_pin_a = 17
motor1_pin_b = 18
motor2_pin_a = 22
motor2_pin_b = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(motor1_pin_a, GPIO.OUT)
GPIO.setup(motor1_pin_b, GPIO.OUT)
GPIO.setup(motor2_pin_a, GPIO.OUT)
GPIO.setup(motor2_pin_b, GPIO.OUT)

def rotate_motors():
    # Rotate motor 1 in one direction
    GPIO.output(motor1_pin_a, GPIO.HIGH)
    GPIO.output(motor1_pin_b, GPIO.LOW)
    
    # Rotate motor 2 in the opposite direction
    GPIO.output(motor2_pin_a, GPIO.LOW)
    GPIO.output(motor2_pin_b, GPIO.HIGH)
    
    # Run the motors for a short period of time
    time.sleep(2)
    
    # Stop the motors
    GPIO.output(motor1_pin_a, GPIO.LOW)
    GPIO.output(motor1_pin_b, GPIO.LOW)
    GPIO.output(motor2_pin_a, GPIO.LOW)
    GPIO.output(motor2_pin_b, GPIO.LOW)

rotate_motors()
