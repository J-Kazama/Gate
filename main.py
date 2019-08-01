# This program operates a smart gate which is embedded on a Raspberry Pi.
# It is implemented with SOPARE to enable voice recognition capabilities.
# Operation algorithms are at the bottom.

import RPi.GPIO as GPIO
import time
import signal
import atexit


# Setting up circuit parts
IN1 = 31
IN2 = 32
IN3 = 33
IN4 = 35

IN1B = 36
IN2B = 37
IN3B = 38
IN4B = 40

DC_CS  = 11
ADC_CLK = 13
ADC_DIO = 12

# Setting up Raspberry Pi's GPIO by their physical location
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(ADC_CS, GPIO.OUT)
GPIO.setup(ADC_CLK, GPIO.OUT)
GPIO.setup(IN1B, GPIO.OUT)
GPIO.setup(IN2B, GPIO.OUT)
GPIO.setup(IN3B, GPIO.OUT)
GPIO.setup(IN4B, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

# Setting up analog to digital converter (ADC)
def setup(cs=11,clk=13,dio=12):
        global ADC_CS, ADC_CLK, ADC_DIO
        ADC_CS=cs
        ADC_CLK=clk
        ADC_DIO=dio

# Setting up stepper motor
# Connecting ADC's output to Raspberry Pi
def getResult(channel=0):
    delay = 0.000002
    GPIO.setup(ADC_DIO, GPIO.OUT)
    GPIO.output(ADC_CS, 0)
    GPIO.output(ADC_CLK, 0)
    GPIO.output(ADC_DIO, 1);  time.sleep(delay)
    GPIO.output(ADC_CLK, 1);  time.sleep(delay)
    GPIO.output(ADC_CLK, 0)
    GPIO.output(ADC_DIO, 1);  time.sleep(delay)
    GPIO.output(ADC_CLK, 1);  time.sleep(delay)
    GPIO.output(ADC_CLK, 0)
    GPIO.output(ADC_DIO, channel);  time.sleep(delay)
    GPIO.output(ADC_CLK, 1)
    GPIO.output(ADC_DIO, 1);  time.sleep(delay)
    GPIO.output(ADC_CLK, 0)
    GPIO.output(ADC_DIO, 1);  time.sleep(delay)
    receiver = 0
    for i in range(0, 8):
        GPIO.output(ADC_CLK, 1);  time.sleep(0.000002)
        GPIO.output(ADC_CLK, 0);  time.sleep(0.000002)
        GPIO.setup(ADC_DIO, GPIO.IN)
        receiver = receiver << 1 | GPIO.input(ADC_DIO)
    receiver2 = 0
    for i in range(0, 8):
        receiver2 = receiver2 | GPIO.input(ADC_DIO) << i
        GPIO.output(ADC_CLK, 1);  time.sleep(0.000002)
        GPIO.output(ADC_CLK, 0);  time.sleep(0.000002)
        GPIO.output(ADC_CS, 1)
        GPIO.setup(ADC_DIO, GPIO.OUT)

        if receiver == receiver2:
            return receiver
        else:
            return 0

# Configuring the GPIOs that receive a digital value
def result():
    return getResult(1)

def setStep(w1, w2, w3, w4):
    GPIO.output(IN1, w1)
    GPIO.output(IN2, w2)
    GPIO.output(IN3, w3)
    GPIO.output(IN4, w4)

def setStepB(w1, w2, w3, w4):
    GPIO.output(IN1B, w1)
    GPIO.output(IN2B, w2)
    GPIO.output(IN3B, w3)
    GPIO.output(IN4B, w4)

# Stepper motor ntialization
def stop():
    setStep(0, 0, 0, 0)

# Gate stepper motor operation: opening
def forward(delay, steps):
    for i in range(0, steps):
        setStep(1, 0, 0, 0)
        time.sleep(delay)
        setStep(0, 1, 0, 0)
        time.sleep(delay)
        setStep(0, 0, 1, 0)
        time.sleep(delay)
        setStep(0, 0, 0, 1)
        time.sleep(delay)

# Gate stepper motor operation: closing
def backward(delay, steps):
    for i in range(0, steps):
        setStep(0, 0, 0, 1)
        time.sleep(delay)
        setStep(0, 0, 1, 0)
        time.sleep(delay)
        setStep(0, 1, 0, 0)
        time.sleep(delay)
        setStep(1, 0, 0, 0)
        time.sleep(delay)

# Locker stepper motor operation: unlocking
def forwardB(delay, steps):
    for i in range(0, steps):
        setStepB(1, 0, 0, 0)
        time.sleep(delay)
        setStepB(0, 1, 0, 0)
        time.sleep(delay)
        setStepB(0, 0, 1, 0)
        time.sleep(delay)
        setStepB(0, 0, 0, 1)
        time.sleep(delay)

# Locker stepper motor operation: locking
def backwardB(delay, steps):
    for i in range(0, steps):
        setStepB(0, 0, 0, 1)
        time.sleep(delay)
        setStepB(0, 0, 1, 0)
        time.sleep(delay)
        setStepB(0, 1, 0, 0)
        time.sleep(delay)
        setStepB(1, 0, 0, 0)
        time.sleep(delay)

# System operation
# fresult & sresult are the readings from
# the IR sensors, a value less than 10
# correlates to sensing an object at the
# gate and the operation begins
def loop():
    while True:
        fresult = getResult(0)
        sresult = getResult(1)
        print 'first result = %d, second result = %d' % (fresult, sresult)
        time.sleep(0.4)

        if fresult  < 10:
                print 'loop arrive'
                time.sleep(0.2)

                # STEPPER UNLOCK
                forwardB(0.004, 128)
                stop()

                # STEPPER OPEN GATE
                backward(0.004, 256)
                stop()
                time.sleep(5)

                # STEPPER CLOSE GATE
                forward(0.004, 256)
                stop()
                time.sleep(0.5)

                # STEPPER LOCK
                backwardB(0.004, 128)
                stop()
                time.sleep(0.5)

                # DELAY BEFORE NEXT GO
                time.sleep(1)

# Stopping the operation
def destroy():
    GPIO.cleanup()

# Starting point of program which sets up the stepper
# motor, ADC, and initializes the operation
if __name__ == '__main__':
    setup()
    try:
        loop()
    # Stop the operation when we hit the keyboard
    except KeyboardInterrupt:
        destroy()
