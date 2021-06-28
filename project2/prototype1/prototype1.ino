
#include <Servo.h>

int numServos = 3;
Servo servos[3];  // create servo object to control a servo
// twelve servo objects can be created on most boards
const int trigPin = 4;
const int echoPin = 3;

float duration, distance;

int pos = 0;    // variable to store the servo position
int incr = 1;
int currentAngle = 0;

void setup() {
  for (int i=0; i<numServos;i++){
    servos[i].attach(9+i);
    
  }
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
//  Serial.print("Test: ");
  Serial.begin(9600);
  
  
}

int getAngleFromDistance() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  noInterrupts();
  duration = pulseIn(echoPin, HIGH);
  interrupts();

  distance = (duration*.0343)/2;
  Serial.print("Distance: ");
  Serial.print(distance);

  int angle = 0;
  if (distance < 45 && distance >= 3) {
    angle = 270/distance;
  } 
  Serial.print(" => Angle: ");
  Serial.println(angle);
  return angle;
}

void loop() {
  
  int newAngle = getAngleFromDistance();
  if (newAngle != currentAngle){
    for (int i=0; i<numServos;i++){
      servos[i].write(newAngle / (i+1));
    }
    currentAngle = newAngle;   
  }
  
  delay(100);
}
