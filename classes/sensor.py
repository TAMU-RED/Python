"""
Base Sensor Class
author: Adam Johnston

Each sensor used in a given test needs to be initialized into this class. The input
can be a Python dict (that can be easily parsed from JSON) so that we can save
sensor information and easily load them by name/model. We can also create a form
in the GUI to create a new sensor and save the information in JSON for later use.

The sensor can be initialized as follows:
    new_sensor = Sensor(**dict)
where dict is the parsed JSON object.

After initialization, the sensor must be attached to a session (see Session class)

TODO: Should everything be stored under sub-sensors?
"""
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr

class Sensor:
    def __init__(self, name, sub_sensors, model, ranges, precisions, thresholds,
                 shutdown_times, conversions, units, documentation, position):
        # Display name of sensor
        self.name = name
        # Name of individual sensors in same order as data output
        self.sub_sensors = sub_sensors
        # Make and model of sensor
        self.model = model
        # Min and max values of sensors of form [min, max]
        self.ranges = ranges
        # Precision of sensor such that +/- 5% -> 0.05
        self.precisions = precisions
        # Min and max safety thresholds of form [min, max]
        self.thresholds = thresholds
        # Number of ms above/below threshold should trigger shutdown [below, above]
        self.shutdown_times = shutdown_times
        # Conversion function given in string form with x as variable as such:
        # '(x - 32) * (5 / 9)'
        # Converted to lambda function
        # If no conversion given, returns raw data
        self.conversions = [sp.lambdify('x', parse_expr(conversion)) if conversion else lambda x: x for conversion in conversions]
        # String representation of units, i.e. 'Pa' or 'K'
        # TODO: Create acceptable list and check against it so that we can
        #       use generic conversion functions as needed
        self.units = units
        # URL to documentation for sensor
        self.documentation = documentation
        # Position for representation on flowchart of form [x, y]
        # NOTE: May not need this here because it is only relevant to GUI
        self.position = position

    # Convert data (i = index of data)
    def convert(self, x, i):
        return self.conversions[i](x)
