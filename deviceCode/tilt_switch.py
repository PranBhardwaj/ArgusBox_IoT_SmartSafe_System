from gpiozero import Button
from time import time

class TiltSwitch:
    def __init__(self, pin, bounce_time=0.1):
        """
        Initializes the tilt switch.
        
        :param pin: GPIO pin number connected to the tilt switch.
        :param bounce_time: Debounce time in seconds.
        """
        self.switch = Button(pin, bounce_time=bounce_time)
        self.state = False  # Default state
        self.last_change_time = time()

        # Set up callbacks for state changes
        self.switch.when_pressed = self._tilt
        self.switch.when_released = self._stable

    def _tilt(self):
        """
        Internal method triggered when the switch is tilted.
        """
        self.state = True
        self.last_change_time = time()

    def _stable(self):
        """
        Internal method triggered when the switch is stable.
        """
        self.state = False
        self.last_change_time = time()

    def get_state(self):
        """
        Returns the current state of the tilt switch.
        
        :return: True if tilted, False otherwise.
        """
        return self.state

    def get_last_change_time(self):
        """
        Returns the last time the switch state changed.
        
        :return: Timestamp of the last state change.
        """
        return self.last_change_time
