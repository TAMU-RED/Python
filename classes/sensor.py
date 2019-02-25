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
"""
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr

class Sensor:
    def __init__(self, name, model, range, precision, threshold,
                 shutdown_time, conversion, units, documentation, position):
        # Display name of sensor
        self.name = name
        # Make and model of sensor
        self.model = model
        # Min and max values of sensor of form [min, max]
        self.range = range
        # Precision of sensor such that +/- 5% -> 0.05
        self.precision = precision
        # Min and max safety thresholds of form [min, max]
        self.threshold = threshold
        # Number of ms above/below threshold should trigger shutdown [below, above]
        self.shutdown_time = shutdown_time
        # Conversion function given in string form with x as variable as such:
        # '(x - 32) * (5 / 9)'
        # Converted to lambda function
        # If no conversion given, returns raw data
        self.convert = sp.lambdify('x', parse_expr(conversion)) if conversion else lambda x: x
        # String representation of units, i.e. 'Pa' or 'K'
        # TODO: Create acceptable list and check against it so that we can
        #       use generic conversion functions as needed
        self.units = units
        # URL to documentation for sensor
        self.documentation = documentation
        # Position for representation on flowchart of form [x, y]
        # NOTE: May not need this here because it is only relevant to GUI
        self.position = position
