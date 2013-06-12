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


class FileAccessException(Exception):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return self.message


class CodeGenerator:
    def __init__(self, json_filename, output_filename, log_handle):
        """
        Initializes CodeGenerator to a usable state.

        :param json_filename: JSON source filename for source code generation
        :type json_filename: :class:`str`
        :param output_filename: Filename of file to write generated source code
        :type output_filename: :class:`str`
        :param log_handle: Logger handle
        :type log_handle: :class:`Logger`
        :raises FileAccessException: Raised when there is an issue accessing
        the JSON source file

        """
        self.json_filename = json_filename
        self.output_filename = output_filename
        self.json_obj = None
        self.classes = []
        self.log_handle = log_handle

        # Parse JSON file. Should't be separated from constructor
        # due to possible concurrency issues.
        try:
            json_file = open(self.json_filename, 'r')
            self.json_obj = json.loads(json_file.read())
            json_file.close()
        except IOError as e:
            raise FileAccessException(
                "Couldn't access JSON source file: {0} - {1}".format(
                    e.errno, e.strerror))

    def log(self, message):
        """
        Add an entry to the log.

        :param message: Message to be added to the log
        :type message: :class:`str`

        """
        if self.log_handle is not None:
            self.log_handle.log(message)

    def write_output(self):
        output_file = open(self.output_filename, 'w')
        for classe in self.classes:
            output_file.write(repr(classe))
        output_file.close()

    def generate_code(self):
        """Entry point for code generation."""
        if self.json_obj is None:
            raise NoClassException('No classes found.')

        for count, obj_class in enumerate(self.json_obj['classes']):
            self.log('Generating all-class methods for {0}'.format(obj_class))
            self.classes.append(Class(obj_class))

            # All methods with the prefix constants.method_generator_prefix
            # should be executed and sent a dictionary containing the object's
            # attributes
            for name, method in inspect.getmembers(
                sys.modules[__name__].CodeGenerator,
                inspect.ismethod):
                if name.startswith(constants.method_generator_prefix) \
                        and name != 'generate_code' \
                        and name != 'generate_template':
                    self.classes[count].add_method_code(
                        method(self,
                               self.json_obj['classes'][obj_class]['attributes'],
                               class_name=obj_class))

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


class Class:
    def __init__(self, name):
        self.name = name
        self.methods = []

    def add_method_code(self, method):
        self.methods.append(method)

    def __repr__(self):
        retval = ("class {class_name}:\n" + 4 * ' ').format(class_name=self.name)
        for method in self.methods:
            method += "\n"
            retval += method.replace('\n', '\n' + 4 * ' ')

        return retval +  "\n"
