from gpiozero import Servo
from time import sleep

servo = Servo(17)

for x in range(-10,10):
    servo.value = x/10.0
    sleep(0.1)

# 
# servo.value = -1
# sleep(0.5)
# servo.value = 1
# sleep(1)
# servo.value = -0.5
# sleep(0.1)
# servo.value = -1
servo.detach()                                                                                                                     
