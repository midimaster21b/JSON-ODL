import sys
import inspect
import json
import constants
from logger import Logger

class NoClassException(Exception):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return self.message

class CodeGenerator:
    def __init__(self, json_filename='test.json', output_filename='test.py',
                 **kwargs):
        self.json_filename = json_filename
        self.output_filename = output_filename
        self.json_obj = None
        if 'log_handle' in kwargs:
            self.log_handle = kwargs['log_handle']
        else:
            self.log_handle = None
        self.parse_json()

    def parse_json(self):
        json_file = open(self.json_filename, 'r')
        self.json_obj = json.loads(json_file.read())
        json_file.close()

    def log(self, message):
        if self.log_handle is not None:
            self.log_handle.log(message)

    # Required Generator
    def generate_code(self):
        methods = []

        if self.json_obj is None:
            raise NoClassException('No classes found.')

        for obj_class in self.json_obj['classes']:
            self.log('Generating all-class methods for: {0}'.format(obj_class))

            # For all methods with the prefix constants.method_generator_prefix
            # should be executed and sent a dictionary containing the object's
            # attributes
            for name, method in inspect.getmembers(sys.modules[__name__].CodeGenerator, inspect.ismethod):
                if name.startswith(constants.method_generator_prefix) \
                        and name != 'generate_code' \
                        and name != 'generate_template':
                    methods.append(method(self, self.json_obj['classes'][obj_class]['attributes']))

            self.log('Generating user-defined methods for: {0}'.format(obj_class))

            # Generate the template code for all methods defined in the json file
            for method_name in self.json_obj['classes'][obj_class]['methods']:
                methods.append(self.generate_template(method_name, self.json_obj['classes'][obj_class]['methods'][method_name]))

            # Print output to screen for testing
            for method in methods:
                print method

    # Required Generator (Generates templates for all methods specified in json)
    def generate_template(self, method_name, method_properties):
        retval = "def {method_name}(self, {method_args}, **kwargs):\n    pass".format(
            method_name=method_name,
            method_args=", ".join(method_properties['args']['required']))

        return retval

    # All-Class Methods (Methods generated for every class)
    def generate_init(self, attributes):
        retval = "def __init__(self, {method_args}, **kwargs):\n".format(
            method_args=", ".join(attributes['required']))
        for attribute in attributes['required']:
            retval += "    self.{0} = {0}\n".format(attribute)

        return retval
