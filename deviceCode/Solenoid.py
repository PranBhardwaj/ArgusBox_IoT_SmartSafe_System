from gpiozero import OutputDevice
import time

class Solenoid:
    def __init__(self, gpio_pin):
        """Initialize the Solenoid class with the GPIO pin connected to the MOSFET gate."""
        self.solenoid_pin = OutputDevice(gpio_pin)  # Set the GPIO pin to control the solenoid (MOSFET gate)
        self.solenoid_pin.off()
    
    def turn_on(self):
        """Activate the solenoid by turning on the MOSFET gate."""
        print("Solenoid is ON.")
        self.solenoid_pin.on()  # Apply 5V to the gate, activating the solenoid
        time.sleep(5)
        self.solenoid_pin.off()
    
    def turn_off(self):
        """Deactivate the solenoid by turning off the MOSFET gate."""
        print("Solenoid is OFF.")
        self.solenoid_pin.off()  # Remove voltage from the gate, deactivating the solenoid
    
    def toggle(self):
        """Toggle the solenoid state (ON to OFF, or OFF to ON)."""
        if self.solenoid_pin.is_active:
            self.turn_off()
        else:
            self.turn_on()

