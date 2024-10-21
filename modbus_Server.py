from pymodbus.datastore import ModbusSlaveContext, ModbusSequentialDataBlock
from pymodbus.server.async_io import StartAsyncTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusServerContext
import asyncio
import logging
import struct
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Helper function to convert string to Modbus registers
def string_to_registers(text):
    # Start with an initial zero register
    registers = [0]  # Start with the index

    # Loop through each character in the input text
    for char in text:
        # Convert character to its decimal value and append to registers
        decimal_value = ord(char)
        registers.append(decimal_value)

    return registers

# Function to execute modbus_client.py when text_value changes
def execute_modbus_client():
    try:
        log.info("Executing modbus_client.py...")
        result = subprocess.run(['python3', 'modbus_client.py'], capture_output=True, text=True)

        # Log the output of modbus_client.py
        log.info(f"modbus_client.py output:\n{result.stdout}")
        if result.stderr:
            log.error(f"modbus_client.py errors:\n{result.stderr}")
    except Exception as e:
        log.error(f"Failed to execute modbus_client.py: {e}")

# Initial text value
text_value = "cowsay hello"  # Change this to store any string
previous_text_value = text_value  # To track changes

async def check_for_text_change():
    global previous_text_value, text_value
    while True:
        # Simulating dynamic change of text_value here
        # In a real application, this might be updated based on some external event or input
        # Uncomment the next line to simulate a change for testing purposes
        # text_value = "new command here" if text_value == "mkdir hello && dir" else "mkdir hello && dir"

        if text_value != previous_text_value:
            log.info(f"text_value changed from '{previous_text_value}' to '{text_value}'")
            registers = string_to_registers(text_value)

            # Update holding registers with new value
            store.setValues(3, 0, registers)

            # Execute modbus_client.py when the text_value changes
            execute_modbus_client()

            previous_text_value = text_value  # Update the previous value to the current one

        await asyncio.sleep(5)  # Check every 5 seconds for a change

# Modbus server setup with holding registers initialized
registers = string_to_registers(text_value)
store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, [0] * 100),  # Discrete Inputs
    co=ModbusSequentialDataBlock(0, [0] * 100),  # Coils
    hr=ModbusSequentialDataBlock(0, registers),  # Holding Registers
    ir=ModbusSequentialDataBlock(0, [0] * 100)   # Input Registers
)
context = ModbusServerContext(slaves=store, single=True)

# Device identification setup
identity = ModbusDeviceIdentification()
identity.VendorName = 'pymodbus'
identity.ProductCode = 'PM'
identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
identity.ProductName = 'pymodbus Server'
identity.ModelName = 'pymodbus Server'
identity.MajorMinorRevision = '3.7.3'

async def run_modbus_server():
    log.info("Starting Modbus server")
    try:
        await StartAsyncTcpServer(
            context=context,
            identity=identity,
            address=("0.0.0.0", 5020)  # Bind to all interfaces on port 5020
        )
    except Exception as e:
        log.error(f"Failed to start the server: {e}")

async def main():
    # Run the Modbus server and check for text_value changes concurrently
    await asyncio.gather(
        run_modbus_server(),
        check_for_text_change()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Server is shutting down...")
    except Exception as e:
        log.error(f"Unexpected error during execution: {e}")
