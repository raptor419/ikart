import RPi.GPIO as GPIO
import time
import numpy
GPIO.setmode(GPIO.BOARD)
GPIO.setup(03, GPIO.OUT)
GPIO.setup(05, GPIO.OUT)
pwm1=GPIO.PWM(03, 50)
pwm1.start(0)
pwm2=GPIO.PWM(05, 50)
pwm2.start(0)
class HX711:
    def __init__(self, dout, pd_sck, gain=128):
        self.PD_SCK = pd_sck
        self.DOUT = dout
        GPIO.setup(self.PD_SCK, GPIO.OUT)
        GPIO.setup(self.DOUT, GPIO.IN)
        self.GAIN = 0
        self.REFERENCE_UNIT = 1  # The value returned by the hx711 that corresponds to your reference unit AFTER dividing by the SCALE.
        self.OFFSET = 1
        self.lastVal = long(0)
        self.LSByte = [2, -1, -1]
        self.MSByte = [0, 3, 1]   
        self.MSBit = [0, 8, 1]
        self.LSBit = [7, -1, -1]
        self.byte_range_values = self.LSByte
        self.bit_range_values = self.MSBit
        self.set_gain(gain)
        time.sleep(1)
    def is_ready(self):
        return GPIO.input(self.DOUT) == 0 or GPIO.input(self.DOUT) == 1
    def set_gain(self, gain):
        if gain is 128:
            self.GAIN = 1
        elif gain is 64:
            self.GAIN = 3
        elif gain is 32:
            self.GAIN = 2
        GPIO.output(self.PD_SCK, False)
        self.read()
    def createBoolList(self, size=8):
        ret = []
        for i in range(size):
            ret.append(False)
        return ret
    def read(self):
        while not self.is_ready():
            print("WAITING")
            print(GPIO.input(self.DOUT))
            pass
        dataBits = [self.createBoolList(), self.createBoolList(), self.createBoolList()]
        dataBytes = [0x0] * 4
        for j in range(self.byte_range_values[0], self.byte_range_values[1], self.byte_range_values[2]):
            for i in range(self.bit_range_values[0], self.bit_range_values[1], self.bit_range_values[2]):
                GPIO.output(self.PD_SCK, True)
                dataBits[j][i] = GPIO.input(self.DOUT)
                GPIO.output(self.PD_SCK, False)
            dataBytes[j] = numpy.packbits(numpy.uint8(dataBits[j]))
        for i in range(self.GAIN):
            GPIO.output(self.PD_SCK, True)
            GPIO.output(self.PD_SCK, False)
        dataBytes[2] ^= 0x80
        return dataBytes

    def get_binary_string(self):
        binary_format = "{0:b}"
        np_arr8 = self.read_np_arr8()
        binary_string = ""
        for i in range(4):
            # binary_segment = binary_format.format(np_arr8[i])
            binary_segment = format(np_arr8[i], '#010b')
            binary_string += binary_segment + " "
        return binary_string

    def get_np_arr8_string(self):
        np_arr8 = self.read_np_arr8()
        np_arr8_string = "[";
        comma = ", "
        for i in range(4):
            if i is 3:
                comma = ""
            np_arr8_string += str(np_arr8[i]) + comma
        np_arr8_string += "]";
        
        return np_arr8_string

    def read_np_arr8(self):
        dataBytes = self.read()
        np_arr8 = numpy.uint8(dataBytes)

        return np_arr8

    def read_long(self):
        np_arr8 = self.read_np_arr8()
        np_arr32 = np_arr8.view('uint32')
        self.lastVal = np_arr32

        return long(self.lastVal)

    def read_average(self, times=3):
        values = long(0)
        for i in range(times):
            values += self.read_long()

        return values / times

    def get_value(self, times=3):
        return self.read_average(times) - self.OFFSET

    def get_weight(self, times=3):
        value = self.get_value(times)
        value = value / self.REFERENCE_UNIT
        return value

    def tare(self, times=15):
        # Backup REFERENCE_UNIT value
        reference_unit = self.REFERENCE_UNIT
        self.set_reference_unit(1)

        value = self.read_average(times)
        self.set_offset(value)
        self.set_reference_unit(reference_unit)

    def set_reading_format(self, byte_format="LSB", bit_format="MSB"):
        if byte_format == "LSB":
            self.byte_range_values = self.LSByte
        elif byte_format == "MSB":
            self.byte_range_values = self.MSByte

        if bit_format == "LSB":
            self.bit_range_values = self.LSBit
        elif bit_format == "MSB":
            self.bit_range_values = self.MSBit

    def set_offset(self, offset):
        self.OFFSET = offset

    def set_reference_unit(self, reference_unit):
        self.REFERENCE_UNIT = reference_unit

    def power_down(self):
        GPIO.output(self.PD_SCK, False)
        GPIO.output(self.PD_SCK, True)
        time.sleep(0.0001)

    def power_up(self):
        GPIO.output(self.PD_SCK, False)
        time.sleep(0.0001)

    def reset(self):
        self.power_down()
        self.power_up()

def SetAngle1(angle):
    duty = angle / 18 + 2
    GPIO.output(03, True)
    pwm1.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(03, False)
    pwm1.ChangeDutyCycle(0)
def doa1():
    SetAngle1(90)
    time.sleep(2)
    SetAngle1(0)
    time.sleep(2)
def SetAngle2(angle):
    duty = angle / 18 + 2
    GPIO.output(05, True)
    pwm2.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(05, False)
    pwm2.ChangeDutyCycle(0)
def doa2():
    SetAngle2(0)
    time.sleep(2)
    SetAngle2(90)
hx1 = HX711(29,31)
hx2 = HX711(33,35)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
while True:
    val1 = max(0, int(hx1.get_weight(5)))
    val2 = max(0, int(hx2.get_weight(5)))
    print (val1,val2)
    hx1.power_down()
    hx1.power_up()
    hx2.power_down()
    hx2.power_up()
    input_state1 = GPIO.input(12)
    if input_state1 == False:
        print('Button 1 Pressed')
        doa1()
        time.sleep(1)
    input_state2 = GPIO.input(18)
    if input_state2 == False:
        print('Button 2 Pressed')
        doa2()
        time.sleep(1)
pwm1.stop()
pwm2.stop()
GPIO.cleanup()
