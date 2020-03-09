from pymodbus.client.sync import ModbusTcpClient

UNIT = 0x1
client = ModbusTcpClient('192.168.0.15', port=50200)

for i in range(0, 10):
    result = client.read_input_registers(16, 10, unit=0x01)
    print(result.registers)
    
    result = client.read_holding_registers(1, 10, unit=0x01)
    print(result.registers)
    
    result = client.write_registers(1, [1, 1, 1, 0, 1],  unit=0x01)
    print(result.isError())

client.close()
