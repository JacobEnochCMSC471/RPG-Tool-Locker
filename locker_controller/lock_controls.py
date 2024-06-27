import serial
from serial import rs485
"""
#--------------------CONSTANTS BEGIN--------------------#
"""
# Hard-coded command that can be sent to the COM Port that will open all locks sequentially 1-24.
full_open_cmd = b'\x8a\x01\x00\x11\x9a'

# Hard-coded command that can be sent to the COM Port to query the status of all doors
query_all_doors = b'\x80\x01\x00\x33\xB2'

# Door unlock values that are used for unlocking specific lockers.
unlock_header = 138  # 0x8A
board_code = 1  # 0x01
fxn_code_unlock = 17  # 0x11

# Lock status query values (int) that are used to query status of individual locks
indv_query_header = 128  # 0x80
indv_query_fxn = 51  # 0x33
open_indicator = 00  # 0x00
closed_indicator = 17  # 0x11, also used to indicate failed unlock sequence for door

# Lock status query for all locks
steps = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]

"""
Each of these represent the value that is added to a running total for 3 groups of 8 doors.
Easy solution to check which doors are open for each group of doors is to convert the returned value into 
binary. This should theoretically tell you which doors are opened and closed for each group. 

Example of returned status value after query: 

80 01 [01 01 01] 33 B3

Convert each of these 3 values into 8-bit binary 

    G3       G2       G1 
[00000001 00000001 00000001] - this tells us that door 1 for all 3 groups (doors 1, 9, 17) are closed, rest are open.


#--------------------CONSTANTS END--------------------#
"""

"""
#--------------------FUNCTIONS START--------------------#
"""


# Generates a code that can be used to query an individual lock's current status
def generate_query_lock_status_code(header: bytes, board_addr: int, lock_addr: int, feedback: bytes,
                                    check_code: bytes) -> bytes:
    # Pattern: header, board_addr, lock_addr, fxn_code, check
    return bytes([header, board_addr, lock_addr, feedback, check_code])


# Checksum at end of unlock command can be calculated by calculating Checksum8 XOR on the full code and
# appending at end of full code for full command
def generate_check_code(header: bytes, board_addr: int, lock_addr: int, lock_state: bytes) -> (bool, int):
    # Pattern: header, board#, lock#, lock state, check code

    check_val_arr = [header, board_addr, lock_state, lock_addr]

    checksum = 0
    try:
        for hex_element in check_val_arr:
            checksum ^= hex_element

        return True, checksum

    except TypeError:
        print('Input number must be some sort of integer representation (binary, hex, decimal).')
        return False, -1


# Generate a hex code string that can be sent to a COM port to unlock an indiv. door
# Can also be used to generate an indiv. query command code - only difference is header + function code
def generate_unlock_code(header: bytes, board_addr: int, lock_addr: int, function_code: bytes) -> (bool, bytes):
    # Pattern: [Cmd header, board address, lock address, fxn_code, check]

    check_code = generate_check_code(header=header,
                                     board_addr=board_addr,
                                     lock_addr=lock_addr,
                                     lock_state=function_code)
    if not check_code[0]:
        print('Check Code < 0. An error has occurred! Check logs.')
        return False, b''

    return True, bytes([header, board_code, lock_addr, function_code, check_code[1]])


# Convert a hex bytestring into binary: b'\x8a\x01\x0b\x00\x80' to a list of 8-bit binary sequences
def bytes_to_binary(byte_str: bytes) -> (bool, list):
    bin_vals = []

    if type(byte_str) != bytes:
        print('Error! These are not bytes.')
        return False, bin_vals

    try:
        # This is from Query All command
        if len(byte_str) == 7:
            #          g1(17-24)     g2(9-16)      g3(1-8)
            groups = [byte_str[2], byte_str[3], byte_str[4]]
            byte_str = groups

        # Return a string that formats hex into 8-bit binary
        # 1 = locked door, 0 = open door for a group of doors
        for byte in byte_str:
            bin_vals.append(''.join(format(byte, '08b')))

        return True, bin_vals

    except TypeError as e1:
        print('Incorrect format for input - check that input is Bytes.')
        print(e1)
        return False, bin_vals


# Send a command to unlock an indiv. door
# Return True, response if the message is sent and a reply is read successfully
# Return False, error_code if exception or port timeout occurs
# Eventually replace all print statements with logging
# Reply format: [cmd_header, board_addr, lock_addr, lock_status, check_code]
def send_command(port: str, command: bytes, cmd_type: str):
    try:
        ser = rs485.RS485(port=port,
                                 baudrate=9600,
                                 stopbits=serial.STOPBITS_ONE,
                                 timeout=0.75,
                                 rtscts=False)

        # UA = Unlock All, UI = Unlock individual, QI = Query Individual, QA = Query All
        if ser.is_open:
            ser.write(command)
            # Response format: [header, board_addr, lock_addr, unlock state, check]
            if cmd_type == 'UI' or cmd_type == 'QI':
                port_resp = ser.read(size=5)

            # Response format: [header, board_addr, state 17-24, state 9-16, state 1-8, fxn_code, check]
            elif cmd_type == 'QA':
                port_resp = ser.read(size=7)

            # Response format seems to be same as code: [header, board_addr, lock_addr, fxn_code, check]
            # b'\x8a\x01\x00\x11\x9a'
            elif cmd_type == 'UA':
                # Give the board time to unlock all boards before responding
                ser.timeout = 10
                port_resp = ser.read(size=5)

            else:
                print('Command not recognized! Check spelling and letter order.')
                return False, -1

            if port_resp:
                print('Data received from port {}'.format(port))
                print('Response: {}'.format(port_resp))
                ser.close()
                return True, port_resp

            else:
                print('Port timeout has occurred, try reconnecting to port {}.'.format(port))
                ser.close()
                return False, -1

    except serial.SerialException as e2:
        print('No data was received from port. Check port connection settings + physical connector.')
        print(e2)
        return False, -1

    except TypeError as e3:
        print('Physical disconnect of USB to RS485 adapter detected, check physical connections.')
        print(e3)
        return False, -1


"""
#--------------------FUNCTIONS END--------------------#
"""

'''
Everything below here is off-the-cuff testing without any real methodology. 
'''
