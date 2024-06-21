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
DXL1_ID = 1  # Dynamixel ID : 1
DXL2_ID = 2  # Dynamixel ID : 2
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
for DXL_ID in [DXL1_ID, DXL2_ID]:
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_MX_TORQUE_ENABLE, TORQUE_ENABLE)
    if dxl_comm_result != COMM_SUCCESS or dxl_error != 0:
        print(f"Failed to enable torque for Dynamixel ID: {DXL_ID}")
        exit()

# Create the main window
root = tk.Tk()
root.title("Dynamixel AX-12A Controller")

# Variables to store the previous goal positions
previous_goal_position1 = -1
previous_goal_position2 = -1


# Function to move Dynamixel to specified position
def move_dynamixel(dxl_id, goal_position):
    goal_position = int(goal_position)
    dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, dxl_id, ADDR_MX_GOAL_POSITION, goal_position)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    else:
        while True:
            dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(portHandler, dxl_id,
                                                                                           ADDR_MX_PRESENT_POSITION)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                break
            elif dxl_error != 0:
                print("%s" % packetHandler.getRxPacketError(dxl_error))
                break
            print(f"ID:{dxl_id} GoalPos:{goal_position}  PresPos:{dxl_present_position}")
            if abs(goal_position - dxl_present_position) < DXL_MOVING_STATUS_THRESHOLD:
                break
            time.sleep(0.1)


# Function to handle slider change
def on_slider_change(event):
    global previous_goal_position1, previous_goal_position2
    goal_position1 = slider1.get()
    goal_position2 = slider2.get()

    if abs(goal_position1 - previous_goal_position1) > 10:  # Change threshold to reduce overload
        move_dynamixel(DXL1_ID, goal_position1)
        previous_goal_position1 = goal_position1

    if abs(goal_position2 - previous_goal_position2) > 10:  # Change threshold to reduce overload
        move_dynamixel(DXL2_ID, goal_position2)
        previous_goal_position2 = goal_position2


# Create GUI components
tk.Label(root, text="Dynamixel 1 Goal Position:").pack()
slider1 = tk.Scale(root, from_=0, to=1023, orient=tk.HORIZONTAL, length=300, command=on_slider_change)
slider1.pack()

tk.Label(root, text="Dynamixel 2 Goal Position:").pack()
slider2 = tk.Scale(root, from_=0, to=1023, orient=tk.HORIZONTAL, length=300, command=on_slider_change)
slider2.pack()

# Run the Tkinter main loop
root.mainloop()

# Disable Dynamixel Torque and close port
for DXL_ID in [DXL1_ID, DXL2_ID]:
    packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_MX_TORQUE_ENABLE, TORQUE_DISABLE)
portHandler.closePort()
