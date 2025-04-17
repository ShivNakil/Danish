import serial
import time

def list_ports():
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def connect_serial(port, baudrate):
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"Connected to {port} at {baudrate} baud.")
        return ser
    except Exception as e:
        print(f"Failed to connect: {e}")
        return None

def send_command(ser, command):
    full_command = f"{command}\r\n".encode()
    ser.write(full_command)
    time.sleep(0.2)
    response = ser.read_all().decode().strip()
    return response

def main():
    print("Available COM Ports:")
    ports = list_ports()
    for idx, port in enumerate(ports):
        print(f"{idx + 1}: {port}")
    
    port_index = int(input("Select COM port number: ")) - 1
    port = ports[port_index]
    
    baudrate = int(input("Enter baudrate (e.g., 9600 or 38400): "))
    ser = connect_serial(port, baudrate)
    if not ser:
        return

    print("Choose parameter to measure:")
    print("1: Voltage")
    print("2: Resistance")
    print("3: Both")
    choice = input("Enter choice (1/2/3): ")

    if choice == "1":
        response = send_command(ser, ":MEAS:VOLT?")
        print("Voltage:", response)
    elif choice == "2":
        response = send_command(ser, ":MEAS:RES?")
        print("Resistance:", response)
    elif choice == "3":
        res = send_command(ser, ":MEAS:RES?")
        volt = send_command(ser, ":MEAS:VOLT?")
        print("Resistance:", res)
        print("Voltage:", volt)
    else:
        print("Invalid choice.")

    ser.close()

if __name__ == "__main__":
    main()
