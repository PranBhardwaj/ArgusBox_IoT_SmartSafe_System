import smbus
import time
import threading

class Keypad:
    def __init__(self, address=0x27, bus_number=1):
        # MCP23017 Register Addresses
        self.MCP23017_IODIRA = 0x00  # GPIO direction (A)
        self.MCP23017_IODIRB = 0x01  # GPIO direction (B)
        self.MCP23017_GPPUA = 0x0C   # Pull-up resistor (A)
        self.MCP23017_GPPUB = 0x0D   # Pull-up resistor (B)
        self.MCP23017_GPIOA = 0x12   # GPIO input/output (A)
        self.MCP23017_GPIOB = 0x13   # GPIO input/output (B)

        # MCP23017 I2C Address
        self.MCP23017_ADDRESS = address  # Adjust as needed for your setup

        # Initialize I2C bus
        self.bus = smbus.SMBus(1)

        # Configure MCP23017
        # Set all A pins (0-7) as inputs
        self.bus.write_byte_data(self.MCP23017_ADDRESS, self.MCP23017_IODIRA, 0xFF)
        # Set all B pins (8-15) as inputs
        self.bus.write_byte_data(self.MCP23017_ADDRESS, self.MCP23017_IODIRB, 0xFF)

        # Enable pull-up resistors for both ports
        self.bus.write_byte_data(self.MCP23017_ADDRESS, self.MCP23017_GPPUA, 0xFF)
        self.bus.write_byte_data(self.MCP23017_ADDRESS, self.MCP23017_GPPUB, 0xFF)

        # Keypad Mapping (adjust for your specific keypad layout)
        self.key_mapping = [
            "*", "7", "4", "1",
            "0", "8", "5", "2",
            "3", "6", "9", "#"  #Inverted line for wiring config
        ]

        self.key_pressed = None

        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()


    def read_keypad(self):

        # Read GPIOA and GPIOB
        gpioa = self.bus.read_byte_data(self.MCP23017_ADDRESS, self.MCP23017_GPIOA)
        gpiob = self.bus.read_byte_data(self.MCP23017_ADDRESS, self.MCP23017_GPIOB)

    # Check each pin for a button press (active LOW)
        for i in range(8):  # Pins 0-7 (Port A)
            if not (gpioa & (1 << i)):
                #print(f"Button {self.key_mapping[i]} pressed pin A{i}")
                self.key_pressed = self.key_mapping[i]
                time.sleep(0.1)

        for i in range(4):  # Pins 8-11 (Port B, mapped as 0-3)
            if not (gpiob & (1 << i)):
                #print(f"Button {self.key_mapping[i + 8]} pressed pin B{i}")
                self.key_pressed = self.key_mapping[i + 8]
                time.sleep(0.1)


    def run(self):
        try:
            while True:
                self.read_keypad()
                time.sleep(0.1)  # Small delay for debounce
        except KeyboardInterrupt:
            print("\nExiting program")



    def get_key(self):
        key = self.key_pressed
        self.key_pressed = None
        return key
        
#"""    

# Example usage:
if __name__ == '__main__':
    keypad = Keypad()
    while True:
        key = keypad.get_key()
        if key:
            print(key)
    

#"""