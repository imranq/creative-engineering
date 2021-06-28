/* Sweep
  by BARRAGAN <http://barraganstudio.com>
  This example code is in the public domain.

  modified 8 Nov 2013
  by Scott Fitzgerald
  http://www.arduino.cc/en/Tutorial/Sweep
*/

#include <Servo.h>

Servo servo1;  // create servo object to control a servo
Servo servo2;
// twelve servo objects can be created on most boards

int pos = 0;    // variable to store the servo position
int incr = 1;


void setup() {
  servo1.attach(3);  // attaches the servo on pin 9 to the servo object
  servo2.attach(2);  // attaches the servo on pin 9 to the servo object
  servo1.write(0);
  servo2.write(180);
}

void loop() {
//  if (pos == 180) {
//    incr = -1;
//  }
//
//  if (pos == 0) {
//    incr = 1;
//  }
//
//  pos += incr;
//  
  servo1.write(0);
  servo2.write(180);
  delay(1000);
  for (pos = 0; pos <= 105; pos += 1) { // goes from 180 degrees to 0 degrees
    servo1.write(pos);
    servo2.write(180-pos); // tell servo to go to position in variable 'pos'
    delay(15);                       // waits 15ms for the servo to reach the position
  }
  delay(2000);
  for (pos = 104; pos >= 0; pos -= 1) { // goes from 180 degrees to 0 degrees
    servo1.write(pos);
    servo2.write(180-pos); // tell servo to go to position in variable 'pos'
    delay(15);                       // waits 15ms for the servo to reach the position
  }

  
}
