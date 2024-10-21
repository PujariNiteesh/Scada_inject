from pymodbus.datastore import ModbusSlaveContext, ModbusSequentialDataBlock
from pymodbus.server.async_io import StartAsyncTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusServerContext
import asyncio
import logging
import struct

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

# Example usage
text_value = "mkdir hello && dir"  # Change this to store any string
registers = string_to_registers(text_value)
print(registers)  # Should output [0, 65]

# Modbus server setup with 10 holding registers initialized
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
    try:
        await run_modbus_server()
    except Exception as e:
        log.error(f"An error occurred in main loop: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Server is shutting down...")
    except Exception as e:
        log.error(f"Unexpected error during execution: {e}")
