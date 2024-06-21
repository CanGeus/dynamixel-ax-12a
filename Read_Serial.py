import serial

# Konfigurasi port serial
ser = serial.Serial('COM3', 9600)

try:
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').rstrip()
            print(data)
except KeyboardInterrupt:
    print("Membaca data dihentikan.")
finally:
    ser.close()
    print("Port serial ditutup.")
