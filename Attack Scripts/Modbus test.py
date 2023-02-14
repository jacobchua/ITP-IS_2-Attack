from pymodbus.client.sync import ModbusTcpClient

# Define Modbus TCP/IP connection settings
ip_address = '127.0.0.1'
port = 502
unit_id = 1

# Create Modbus TCP/IP client
client = ModbusTcpClient(ip_address, port)

# Connect to Modbus device
client.connect()

# Read holding registers
starting_address = 0
quantity = 10
result = client.read_holding_registers(starting_address, quantity, unit=unit_id)

# Print results
if not result.isError():
    data = result.registers
    print(f'Read {quantity} holding registers starting at address {starting_address}: {data}')
else:
    print(f'Error reading holding registers: {result}')
    
# Disconnect from Modbus device
client.close()