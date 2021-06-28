/*
 * HC-SR04 example sketch
 *
 * https://create.arduino.cc/projecthub/Isaac100/getting-started-with-the-hc-sr04-ultrasonic-sensor-036380
 *
 * by Isaac100
 */

const int trigPin = 7;
const int echoPin = 6;

float duration, distance;

void setup() {
//  Serial.print("Test: ");
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
//  Serial.print("Test: ");
  Serial.begin(9600);
}

void loop() {
//  Serial.print("Distance: ");
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  distance = (duration*.0343)/2;
  Serial.print("Distance: ");
  Serial.println(distance);
  delay(100);
}
