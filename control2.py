import os
import time
import tkinter as tk
from dynamixel_sdk import *  # Uses Dynamixel SDK library

# Control table address
ADDR_MX_TORQUE_ENABLE = 24
ADDR_MX_GOAL_POSITION = 30
ADDR_MX_PRESENT_POSITION = 36

# Protocol version
PROTOCOL_VERSION = 1.0

# Default setting
DXL_ID = 1
BAUDRATE = 1000000
DEVICENAME = 'COM9'

TORQUE_ENABLE = 1
TORQUE_DISABLE = 0
DXL_MOVING_STATUS_THRESHOLD = 20

# Initialize PortHandler instance
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Open port
if not portHandler.openPort():
    print("Failed to open the port")
    exit()

# Set port baudrate
if not portHandler.setBaudRate(BAUDRATE):
    print("Failed to change the baudrate")
    exit()

# Enable Dynamixel Torque
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_MX_TORQUE_ENABLE, TORQUE_ENABLE)
if dxl_comm_result != COMM_SUCCESS or dxl_error != 0:
    print("Failed to enable torque")
    exit()

# Create the main window
root = tk.Tk()
root.title("Dynamixel AX-12A Controller")

# Function to move Dynamixel to specified position
def move_dynamixel(goal_position):
    goal_position = int(goal_position)
    dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, DXL_ID, ADDR_MX_GOAL_POSITION, goal_position)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    else:
        while True:
            dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(portHandler, DXL_ID, ADDR_MX_PRESENT_POSITION)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                break
            elif dxl_error != 0:
                print("%s" % packetHandler.getRxPacketError(dxl_error))
                break
            print(f"GoalPos:{goal_position}  PresPos:{dxl_present_position}")
            if abs(goal_position - dxl_present_position) < DXL_MOVING_STATUS_THRESHOLD:
                break
            time.sleep(0.1)

# Function to handle button click
def on_move_button_click():
    goal_position = goal_position_entry.get()
    move_dynamixel(goal_position)

# Create GUI components
tk.Label(root, text="Goal Position:").pack()
goal_position_entry = tk.Entry(root)
goal_position_entry.pack()
move_button = tk.Button(root, text="Move", command=on_move_button_click)
move_button.pack()

# Run the Tkinter main loop
root.mainloop()

# Disable Dynamixel Torque and close port
packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_MX_TORQUE_ENABLE, TORQUE_DISABLE)
portHandler.closePort()
