/* Sweep
  by BARRAGAN <http://barraganstudio.com>
  This example code is in the public domain.

  modified 8 Nov 2013
  by Scott Fitzgerald
  http://www.arduino.cc/en/Tutorial/Sweep
*/

#include <Servo.h>

Servo servos[2];  // create servo object to control a servo

int pos = 0;    // variable to store the servo position

void setup() {
  for(int i=0;i<2;i++){
    servos[i].attach(9+i);
  }
}

void writeToAllServos(int angle) {
  for(int i=0;i<2;i++){
      if(i % 2 == 0 ) {
        servos[i].write(angle);  
      } else {
        servos[i].write(90-angle);  
      }
  }
}


void loop() {
//myservo.write(pos);
  for (pos =  0; pos <= 40; pos += 1) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    writeToAllServos(pos);
    delay(20);                       // waits 15ms for the servo to reach the position
  }
  for (pos = 39; pos >= 0; pos -= 1) { // goes from 180 degrees to 0 degrees
    writeToAllServos(pos);
    delay(20);                       // waits 15ms for the servo to reach the position
  }
}
