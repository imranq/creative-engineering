
#include <Servo.h>

Servo servo1;  // create servo object to control a servo
Servo servo2;
// twelve servo objects can be created on most boards

int pos = 0;    // variable to store the servo position
int incr = 1;

const int trigPin = 7;
const int echoPin = 6;
const int MAXANGLE = 105;
const int TOLERANCE = 0.1;
const int MAXDIST = 25; //cm
const int MINDIST = 20; //cm
int HISTORYLEN = 5;
bool frameOpen = false;
int MAXDISTANCEREADING = 3000;
int MINDISTANCEREADING = 1;





void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  Serial.begin(9600);
}

float getDistance() {
  float duration, distance;
  
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
  Serial.println(distance);
  delay(100);
  return distance;
}

float getDistanceWithoutOutliers() {
  float t_avg = 0.0;  //or double for higher precision
  float sumDistance = 0.0;
  float avg = 0.0; 
  float distances[HISTORYLEN];
 
  for (int i = 0 ; i < HISTORYLEN; i++){
    distances[i] = getDistance();
    sumDistance += distances[i];
  }

  t_avg = sumDistance / HISTORYLEN;
  sumDistance = 0.0;
  int countMax = 0;
  
  //now get the average without the outliers
  for (int i = 0 ; i < HISTORYLEN; i++){
    if (distances[i] < MAXDISTANCEREADING) {
      sumDistance += distances[i];
    } else {
      countMax += 1;
    }
  }

  avg = sumDistance / HISTORYLEN;

  if (countMax >= HISTORYLEN-1) {
    return MAXDISTANCEREADING;
  } else {
    return avg;    
  }
  
}


float getAngleFromDistance(float distance) {
  float angle = 0;
  if (distance < MAXDIST && distance > MINDIST) {
    angle = MAXANGLE*MINDIST/distance;
    angle = 0;
  } else if (distance <= MINDIST && distance >= 3) {
    angle = MAXANGLE;
  }
  return angle;
}

void writeToServos(int a, int b){
  if (a < b) {
    for (int i = a; i <= b; i++){
      servo1.write(i);
      servo2.write(180-i);  
      delay(20);
    }  
  } else if (a > b) {
    for (int i = a; i >= b; i--){
      servo1.write(i);
      servo2.write(180-i);  
      delay(20);
    }  
  }
  
}

void openFrame() {
  servo1.attach(3);  
  servo2.attach(2);  
  writeToServos(0, MAXANGLE);
  frameOpen = true;
  
  servo1.detach();  
  servo2.detach();
}

void closeFrame() {
  
  servo1.attach(3);  
  servo2.attach(2);  
  writeToServos(MAXANGLE, 0);
  frameOpen = false;
  
  servo1.detach();  
  servo2.detach();
}


void loop() {
  //if the reading is greater than the tolerance of the average then reject the reading
  float t_dist = getDistanceWithoutOutliers();
  Serial.print("Average FILTERED Distance: ");
  Serial.println(t_dist);


  if (t_dist <= MINDIST && t_dist > MINDISTANCEREADING && frameOpen == false) {
    openFrame();
  } else if (t_dist > MINDIST && frameOpen == true) {
    closeFrame();
  } else if (t_dist < MINDISTANCEREADING && frameOpen == true) {
    closeFrame();
  }
  
}
