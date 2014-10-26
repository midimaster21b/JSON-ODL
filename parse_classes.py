import sys
import inspect
import json

import constants
from logger import Logger
from interfaces import Class, Method, Property


class CodeGenerator:
    def __init__(self, logger=None):
        """
        Initializes CodeGenerator to a usable state.

        :param logger: Logger handle
        :type logger: :class:`Logger`

        """
        self.classes = []
        if logger is not None:
            self._logger = logger
        else:
            self._logger = Logger(constants.default_logger_filename)

    def log(self, message):
        """
        Add an entry to the log.

        :param message: Message to be added to the log
        :type message: :class:`str`

        """
        if self._logger is not None:
            self._logger.log(message)

    def save_generated_source_code(self, filename):
        """
        Save generated source code to output file.

        :param filename: Name of file to write source code
        :type filename: :class:`str`

        """
        output_file = open(filename, 'w')
        for generated_class in self.classes:
            output_file.write(str(generated_class))
        output_file.close()

    def parse_to_objects(self, JSON):
        """
        Parse json and generate Class classes.

        :param JSON: JSON to be parsed
        :type JSON: :class:`str`
        :return: Dictionary of Class classes
        :rtype: :class:`dictionary` of :class:`Class`

        """
        json_obj = json.loads(JSON)
        for classname in json_obj['classes']:
            json_obj['classes'][classname]


    def generate_code(self, JSON):
        """
        Entry point for code generation.

        :param JSON: JSON to be parsed
        :type JSON: :class:`str`

        """

        for count, obj_class in enumerate(self.json_obj['classes']):
            self.log('Generating all-class methods for {0}'.format(obj_class))
            self.classes.append(Class(obj_class))


            self.log('Generating user-defined methods for {0}'.format(obj_class))

            # Generate the template code for all methods defined in the json file
            for method_name in self.json_obj['classes'][obj_class]['methods']:
                self.classes[count].add_method_code(
                    self.generate_template(
                        method_name,
                        self.json_obj['classes'][obj_class]['methods'][method_name]))

            # Generate code for additional methods defined in constants file
            for module in constants.additional_method_modules:
                try:
                    __import__(module)
                    self.log('Generating additional methods defined in {0} for {1}'.format(
                            module,
                            obj_class))

                    for name, method in inspect.getmembers(
                        sys.modules[module],
                        inspect.isfunction): # MUST BE inspect.isfunction
                        if name.startswith(constants.method_generator_prefix):
                            self.classes[count].add_method_code(
                                method(obj_class,
                                       self.json_obj['classes'][obj_class]['attributes']))

                except KeyError:
                    self.log('Could not find module {0} within sys.modules'.format(module))

                except ImportError:
                    self.log('Could not import module {0}'.format(module))

            self.log("Finished generating methods for {0}\n\n".format(obj_class))

    # NOT FINISHED YET!!!
    def inspect_immediate_module(class_object, method_prefix):
        """
        Find and execute all methods with the prefix method_generator_prefix
        (as defined in the file constants.py) and send a dictionary containing
        the object's attributes.

        :param class_object: Class object containing all the class info
        :type class_object: :class:`Class`
        :param json_obj: Object containing all json to be used

        """
        for name, method in inspect.getmembers(
            sys.modules[__name__].CodeGenerator,
            inspect.ismethod):
            if name.startswith(method_prefix) \
                    and name != 'generate_code' \
                    and name != 'generate_template':
                self.classes[count].add_method_code(
                    method(self,
                           self.json_obj['classes'][obj_class]['attributes'],
                           class_name=obj_class))


    def generate_template(self, method_name, method_properties):
        """Generate templates for all methods specified in json model description.

        This method is required."""
        retval = """def {method_name}(self, {method_args}, **kwargs):
    pass\n""".format(
            method_name=method_name,
            method_args=", ".join(method_properties['args']['required']))

        return retval

    # All-Class Methods (Methods generated for every class)
    def generate_init(self, attributes, **kwargs):
        """Generate __init__ method."""
        retval = "def __init__(self, {method_args}, **kwargs):\n".format(
            method_args=", ".join(attributes['required']))
        for attribute in attributes['required']:
            retval += "    self.{0} = {0}\n".format(attribute)

        return retval

    def generate_repr(self, attributes, **kwargs):
        """Generate __repr__ method."""
        retval = """def __repr__(self):
    return '{class_name}(""".format(class_name=kwargs['class_name'] if 'class_name' in kwargs else '')
        retval += "({" + "}, {".join(str(x) for x in range(0, len(attributes['required']))) + "})'.format(self."
        retval += ", self.".join(attributes['required']) + ")\n"

        return retval
