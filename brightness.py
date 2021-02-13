import math
import os
import time


DRIVER_ROOT = '/sys/class/backlight/intel_backlight/'
BRIGHTNESS_CONFIG_FILE = os.path.join(DRIVER_ROOT, 'brightness')
BRIGHTNESS_MAX_REFERENCE_FILE = os.path.join(DRIVER_ROOT, 'max_brightness')
BRIGHTNESS_STEP = 25
BRIGHTNESS_MIN = 1


class BrightnessControl:
    def __init__(self):
        super().__init__()
        if self.has_backlight():
            with open(BRIGHTNESS_MAX_REFERENCE_FILE) as file:
                self._brightness_max = int(file.read().strip())
        else:
            self._brightness_max = 0
        self.change_in_progress = False

    @staticmethod
    def has_backlight():
        return os.path.exists(BRIGHTNESS_MAX_REFERENCE_FILE)

    @property
    def max_brightness(self):
        return self._brightness_max

    @staticmethod
    def validate_and_sanitize_brightness_value(value):
        assert (isinstance(value, int) or isinstance(value, float)),\
            'brightness must be either int or float'

        if value < 1:
            return 1
        if value > 100:
            return 100
        return value

    def percent_to_internal(self, percent):
        validated = self.validate_and_sanitize_brightness_value(percent)
        return int((validated / 100) * self.max_brightness)

    @property
    def brightness_current(self):
        with open(BRIGHTNESS_CONFIG_FILE) as config_file:
            return int(config_file.read().strip())

    @staticmethod
    def write_brightness_value(value):
        with open(BRIGHTNESS_CONFIG_FILE, 'w') as config_file:
            config_file.write(str(value))

    def _set(self, percent):
        brightness_requested = self.percent_to_internal(percent)
        # Abort any in progress change
        self.change_in_progress = False

        brightness = self.brightness_current

        self.change_in_progress = True
        if brightness_requested > brightness:
            decimal_steps, full_steps = math.modf((brightness_requested - brightness) / BRIGHTNESS_STEP)
            for i in range(int(full_steps)):
                if not self.change_in_progress:
                    break
                brightness += BRIGHTNESS_STEP
                self.write_brightness_value(brightness)
                time.sleep(0.02)
            if self.change_in_progress:
                brightness += int(decimal_steps * BRIGHTNESS_STEP)
                self.write_brightness_value(brightness)
        else:
            decimal_steps, full_steps = math.modf((brightness - brightness_requested) / BRIGHTNESS_STEP)
            for i in range(int(full_steps)):
                if not self.change_in_progress:
                    break
                brightness -= BRIGHTNESS_STEP
                self.write_brightness_value(brightness)
                time.sleep(0.02)
            if self.change_in_progress:
                brightness -= int(decimal_steps * BRIGHTNESS_STEP)
                self.write_brightness_value(brightness)

        # Ensure brightness is correct at the end
        if brightness != brightness_requested:
            self.write_brightness_value(brightness_requested)

        self.change_in_progress = False

