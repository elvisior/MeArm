
#include <NewPing.h>

#define TRIGGER_PIN  12  // Arduino pin tied to trigger pin on the ultrasonic sensor.
#define ECHO_PIN     3  // Arduino pin tied to echo pin on the ultrasonic sensor.
#define MAX_DISTANCE 140 // Maximum distance we want to ping for (in centimeters). Maximum sensor distance is rated at 400-500cm.
String output="";
NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); // NewPing setup of pins and maximum distance.

#include <Servo.h> 
//MeArm HAS 4 SERVOS
Servo xServo;  // create servo object, arm base servo - left right motion
Servo yServo;  // create servo object, left side servo - forward backwards motion
Servo zServo;  // create servo object, right side servo - forward backwards motion
Servo clawServo;  // create servo object, end of arm srevo - open,close the claw hand
 
//servo positions values, expects 1-180 deg.
int xPos;
int yPos;
int zPos;
int clawPos;
String location="";
 
//*************** INIT AT STARTUP *******************************************************************
 
void setup() {        // the setup function runs once when you press reset or power the board
 
  // assign servo to pin numbers
  xServo.attach(11);  // attaches the servo on pin 11 to the servo object
  yServo.attach(10);  // attaches the servo on pin 10 to the servo object
  zServo.attach(9);  // attaches the servo on pin 9 to the servo object
  clawServo.attach(6);  // attaches the servo on pin 6 to the servo object
 
  // initialize serial port
  Serial.begin(115200);
 
  // Debug only send serial message to host com port terminal window in Arduino IDE
  //Serial.print("*** MeCom Test V04 ***.");   // send program name, uncomment for debug connection test
 location = String("Location: " + String(xServo.read()) + "," + String(yServo.read()) + "," + String(zServo.read()) + "," + String(clawServo.read()) + "\n");
 Serial.print(location);
 
 
}
 
// ******************************************************************************************************
// ********************************** MAIN PROGRAM LOOP START *******************************************
// ******************************************************************************************************
 
void loop() {
 

  //serial in packet patern = xVal,yVal,zVal,clawVal + end of packet char '\n'
  while (Serial.available() > 0) {
    xPos = Serial.parseInt();
    yPos = Serial.parseInt();
    zPos = Serial.parseInt();
    clawPos = Serial.parseInt();
 
    if (Serial.read() == '\n') { // Detect end of packet char '\n', go ahead and update servo positions
 
 
      // UPDATE SERVO POSITIONS
      xServo.write(xPos);
      yServo.write(yPos);
      zServo.write(zPos);
      clawServo.write(clawPos);
      delay(50);
      location = String("Location: " + String(xServo.read()) + "," + String(yServo.read()) + "," + String(zServo.read()) + "," + String(clawServo.read()) + " ");
      Serial.print(location);
      float uS = sonar.ping(); // Send ping, get ping time in microseconds (uS).
      output = String("Ping: " + String(uS / US_ROUNDTRIP_CM) + " cm\n"); // Convert ping time to distance and print result (0 = outside set distance range, no ping echo)
      Serial.print(output);
    }
 
  }
  //location = String("Location: " + String(xServo.read()) + "," + String(yServo.read()) + "," + String(zServo.read()) + "," + String(clawServo.read()) + "\n");
  //Serial.print(location);
}
