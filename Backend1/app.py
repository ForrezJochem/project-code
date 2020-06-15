# pylint: skip-file
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219
from repositories.DataRepository import DataRepository
from repositories.SERIAL import SERIAL
from flask_socketio import SocketIO
from subprocess import check_output
from repositories.SEND import SEND
from repositories.ADC import ADC
from flask import Flask, jsonify
from flask_cors import CORS
import struct
import board
import time
import threading


from RPi import GPIO


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
SERIAL = SERIAL(27)
send = SEND()
GPIO.setup(16, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
servoX = GPIO.PWM(13, 50)
servoY = GPIO.PWM(16, 50)
servoX_value = 2.5
servoY_value = 2.5
servoX.start(servoX_value)
servoY.start(servoY_value)
servoX_value_old = 2.5
servoY_value_old = 2.5
time.sleep(2)
ldr = {"lb": 0,"rb": 0,"lo": 0,"ro":0}
adc = ADC(10 ** 5)
offset = 15
ldr_counter = 0
i2c_bus = board.I2C()
manual_mode = 0
ip_old = ""
 
solar = INA219(i2c_bus, 0x41)
battery = INA219(i2c_bus, 0x40)

def get_all_ldr():
    ldr["lb"] = adc.analogRead(0)
    ldr["lo"] = adc.analogRead(1)
    ldr["rb"] = adc.analogRead(2)
    ldr["ro"] = adc.analogRead(3)
    servo_move(ldr)


def get_ip_print_to_display():
    global ip_old
    ips = str(check_output(['hostname', '-I']))
    ipslist = ips.replace("b'", "").split(" ")
    k=struct.pack('B', 0xff)
    SERIAL.send_action(b"t0.txt=")
    SERIAL.send('"')
    SERIAL.send(ipslist[1])
    SERIAL.send('"')
    SERIAL.send_action(k)
    SERIAL.send_action(k)
    SERIAL.send_action(k)
    print(f"ip set {ipslist[0]}")

def servo_move(ldr):
    global manual_mode
    global servoX_value
    global servoY_value
    global servoX_value_old
    global servoY_value_old
    global offset
    global ldr_counter
    global manual_mode
    if manual_mode == 0:
        if ldr["rb"] > ldr["lb"] and abs(ldr["rb"]- ldr["lb"]) > offset:
            servoX_value += 0.025
            if servoX_value > 12.5:
                servoX_value = 12.5
                print("servoX einde")
        elif ldr["lb"] > ldr["rb"] and abs(ldr["rb"]- ldr["lb"]) > offset:
            servoX_value -= 0.025
            if servoX_value < 2.5:
                servoX_value = 2.5
                print("servoX einde")
        if ldr["lo"] > ldr["lb"] and abs(ldr["lo"]- ldr["lb"]) > offset:
            servoY_value -= 0.025
            if servoY_value < 2.5:
                servoY_value = 2.5
                print("servoY einde")
        elif ldr["lb"] > ldr["lo"] and abs(ldr["lo"]- ldr["lb"]) > offset:
            servoY_value += 0.025
            if servoY_value > 12.5:
                servoY_value = 12.5
                print("servoY einde")
        print(f"servoX:{servoX_value}")
        print(f"servoY:{servoY_value}")
        if servoX_value != servoX_value_old:
            servoX.start(servoX_value)
            servoX_value_old = servoX_value
        if servoY_value != servoY_value_old:
            servoY.start(servoY_value)
            servoY_value_old = servoY_value
        time.sleep(0.025)
        ldr_counter += 1
        if ldr_counter > 99:
            get_ip_print_to_display()
            print("to data bank")
            ldr_counter = 0
            threading.Thread(target=sensor_to_databank).start()
    


def translate(value, input_min, input_max, output_min, output_max):
    input_range = input_max - input_min
    output_range = output_max - output_min
    valueScaled = float(value - input_min) / float(input_range)
    return output_min + (valueScaled * output_range)


def sensor_to_databank():
    DataRepository.append_waarde_sensor(5,ldr["lb"])
    DataRepository.append_waarde_sensor(6,ldr["lo"])
    DataRepository.append_waarde_sensor(7,ldr["rb"])
    DataRepository.append_waarde_sensor(8,ldr["ro"])
    solar_voltage = solar.bus_voltage
    DataRepository.append_waarde_sensor(3, solar_voltage)
    battery_voltage = battery.bus_voltage
    DataRepository.append_waarde_sensor(4, battery_voltage)
    solar_current = solar.current
    DataRepository.append_waarde_sensor(9, solar_current)
    battery_current = battery.current
    DataRepository.append_waarde_sensor(10, battery_current)
    DataRepository.update_pos_actuator("x",translate(servoX_value, 2.5, 12.5, 1, 180))
    DataRepository.update_pos_actuator("y",translate(servoY_value, 2.5, 12.5, 1, 180))


def data():
    try:
        get_ip_print_to_display()
        while True:
            get_all_ldr()
            
    except KeyboardInterrupt as e:
        print(e)
        print("script stopt")
        GPIO.cleanup()

get_ip_print_to_display()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key :)'

endpoint = '/api/v1'

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)


# API ENDPOINTS
@app.route('/')
def hallo():
    return "Server is running, er zijn momenteel geen API endpoints beschikbaar."


@app.route(endpoint + '/sensor', methods=['GET'])
def get_sensor():
    return jsonify( data1=DataRepository.read_sensor(5, 250), data2=DataRepository.read_sensor(6, 250), data3=DataRepository.read_sensor(7, 250), data4=DataRepository.read_sensor(8, 250) ),200


# SOCKET IO
@socketio.on('connect')
def initial_connection():
    print('A new client connect')

@socketio.on("F2B_home_connect")
def send_graph_data():
    data1 = DataRepository.read_sensor(5, 50)
    while data1 == None:
        data1 = DataRepository.read_sensor(5, 50)
    socketio.emit('B2F_verandering_graph_ldr', data1)
    data2 = DataRepository.read_sensor(6, 50)
    while data2 == None:
        data2 = DataRepository.read_sensor(6, 50)
    socketio.emit('B2F_verandering_graph_ldr', data2)
    data3 = DataRepository.read_sensor(7, 50)
    while data3 == None:
        data3 = DataRepository.read_sensor(7, 50)
    socketio.emit('B2F_verandering_graph_ldr', data3)
    data4 = DataRepository.read_sensor(8, 50)
    while data4 == None:
        data4 = DataRepository.read_sensor(8, 50)
    socketio.emit('B2F_verandering_graph_ldr', data4)
    data5 = DataRepository.read_sensor(3,50)
    while data5 == None:
        data5 = DataRepository.read_sensor(3,50)
    socketio.emit('B2F_verandering_graph_solar', data5)
    data6 = DataRepository.read_sensor(9,50)
    while data6 == None:
        data6 = DataRepository.read_sensor(9,50)
    socketio.emit('B2F_verandering_graph_solar', data6)
    data7 = DataRepository.read_sensor(4,50)
    while data7 == None:
        data7 = DataRepository.read_sensor(4,50)
    socketio.emit('B2F_verandering_graph_solar', data7)
    data8 = DataRepository.read_sensor(10,50)
    while data8 == None:
        data8 = DataRepository.read_sensor(10,50)
    socketio.emit('B2F_verandering_graph_solar', data8)

@socketio.on("F2B_Manual_Mode_change")
def change_setting(object):
    global manual_mode
    print(object["setting"])
    print(object["value"])
    DataRepository.update_setting(object["setting"], object["value"])
    if object["value"] == 1:
        print("1")
        manual_mode = 1
    else:
        print("0")
        manual_mode = 0

@socketio.on("F2B_servoX")
def change_servoX(value):
    global manual_mode
    global servoX_value
    print(value)
    if manual_mode == 1:
        value = float(value)
        servoX.start(value)
        servoY_value = value


@socketio.on("F2B_servoY")
def change_servoY(value):
    global manual_mode
    global servoY_value
    print(value)
    if manual_mode == 1:
        value = float(value)
        servoY.start(value)
        servoX_value = value
    

threading.Thread(target=data).start()


if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')

