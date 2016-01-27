#include <NewPing.h>

#define VALVE_PIN 13 // Arduino pin tied to trigger pin for the air pump's valve
#define PUMP_PIN 7   // Arduino pin tied to trigger pin for the air pump
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
int valve_state=0;
int pump_state=0;
int xPos;
int yPos;
int zPos;
int clawPos;
int pumpPos;
String location="";
 
//*************** INIT AT STARTUP *******************************************************************
 
void setup() {        // the setup function runs once when you press reset or power the board
 
  // assign servo to pin numbers
  xServo.attach(11);  // attaches the servo on pin 11 to the servo object
  yServo.attach(10);  // attaches the servo on pin 10 to the servo object
  zServo.attach(9);  // attaches the servo on pin 9 to the servo object
  clawServo.attach(6);  // attaches the servo on pin 6 to the servo object

  pinMode(VALVE_PIN, OUTPUT); //VALVE_PIN
  pinMode(PUMP_PIN, OUTPUT); //PUMP_PIN
 
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
  int notthere;
  int tmpx, tmpy, tmpz, tmpc;
  
  //serial in packet patern = xVal,yVal,zVal,clawVal + end of packet char '\n'
  while (Serial.available() > 0) {
    notthere=1;
    xPos = Serial.parseInt();
    yPos = Serial.parseInt();
    zPos = Serial.parseInt();
    clawPos = Serial.parseInt();
    pumpPos = Serial.parseInt();
 
    if (Serial.read() == '\n') { // Detect end of packet char '\n', go ahead and update servo positions
 
 
      // UPDATE SERVO POSITIONS

      tmpx=xServo.read();
      tmpy=yServo.read();
      tmpz=zServo.read();
      tmpc=clawServo.read();
      while(notthere){
        //shuffle x along
        if(tmpx>xPos){
          tmpx=tmpx-1;
        }
        if(tmpx<xPos){
          tmpx=tmpx+1;
        }
        //shuffle y along
        if(tmpy>yPos){
          tmpy=tmpy-1;
        }
        if(tmpy<yPos){
          tmpy=tmpy+1;
        }  
        //shuffle z along
        if(tmpz>zPos){
          tmpz=tmpz-1;
        }
        if(tmpz<zPos){
          tmpz=tmpz+1;
        }  
        //shuffle c along
        if(tmpc>clawPos){
          tmpc=tmpc-1;
        }
        /*
        if(tmpc<cPos){
          tmpc=tmpc+1;
        }
        */
        //check if we are there yet
        //if(tmpx==xPos && tmpy==yPos && tmpz==zPos && tmpc==clawPos){
        if(tmpx==xPos && tmpy==yPos && tmpz==zPos){
          notthere=0;
        }
        else{
          notthere=1;
        }
        xServo.write(tmpx);
        yServo.write(tmpy);
        zServo.write(tmpz);
        clawServo.write(tmpc);
        delay(5);
      }
      
      xServo.write(xPos);
      yServo.write(yPos);
      zServo.write(zPos);
      clawServo.write(clawPos);
      
      if(pumpPos==1){
          digitalWrite(VALVE_PIN, LOW);//VALVE_PIN stop
          digitalWrite(PUMP_PIN, HIGH);//PUMP_PIN work
      }
      else{
          digitalWrite(VALVE_PIN, HIGH);//VALVE_PIN work
          digitalWrite(PUMP_PIN, LOW);//PUMP_PIN stop        
      }
      delay(50);
      location = String("Location: " + String(xServo.read()) + "," + String(yServo.read()) + "," + String(zServo.read()) + "," + String(clawServo.read()) + " ");
      Serial.print(location);
      float uS = sonar.ping(); // Send ping, get ping time in microseconds (uS).
      output = String("Ping: " + String(uS / US_ROUNDTRIP_CM) + " cm\n"); // Convert ping time to distance and print result (0 = outside set distance range, no ping echo)
      Serial.print(output);
      output = String("\n");
      Serial.print(output);
    }
 
  }
  //location = String("Location: " + String(xServo.read()) + "," + String(yServo.read()) + "," + String(zServo.read()) + "," + String(clawServo.read()) + "\n");
  //Serial.print(location);
}
