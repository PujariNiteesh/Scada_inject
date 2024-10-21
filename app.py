from flask import Flask, render_template
from pymodbus.client import AsyncModbusTcpClient
import asyncio
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Modbus server parameters
MODBUS_SERVER_IP = '127.0.0.1'
MODBUS_SERVER_PORT = 5020

# Asynchronous function to read holding registers
async def read_holding_registers(address, count):
    async with AsyncModbusTcpClient(MODBUS_SERVER_IP, port=MODBUS_SERVER_PORT) as client:
        log.info(f"Connecting to Modbus server at {MODBUS_SERVER_IP}:{MODBUS_SERVER_PORT}")
        
        result = await client.read_holding_registers(address, count)
        
        if result.isError():
            log.error(f"Modbus Error: {result}")
            return None
        
        return result.registers

# Synchronous wrapper to call the async function
def sync_read_holding_registers(address, count):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(read_holding_registers(address, count))

def registers_to_string(registers):
    """Convert the register values to characters and return the resulting string."""
    characters = [chr(value) for value in registers]  # Use value directly since they are already integers
    result_string = ''.join(characters)
    return result_string

@app.route('/')
def index():
    address = 0  # Change to the desired starting address
    count = 5    # Change to the desired count of registers
    values = sync_read_holding_registers(address, count)

    if values is not None:
        log.info(f"Read values: {values}")
        log.info(f"registers_to_string: {registers_to_string(values):}")
    else:
        log.error("Failed to read registers.")
    
    return render_template('index.html', values=values)

if __name__ == '__main__':
    app.run(debug=True)
