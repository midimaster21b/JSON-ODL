class InterfaceException(Exception):
    def __init__(self, exception_message):
        self.exception_message = exception_message

    def __str__(self):
        return 'Error: {0}'.format(self.exception_message)


class Class:
    def __init__(self, name):
        self.name = name
        self.methods = {}
        self.properties = {}

    def add_method(self, method_name, method_object):
        self.methods[method_name] = method_code

    def add_property(self, property_name, property_object):
        self.properties[property_name] = property_object

    def __repr__(self):
        raise InterfaceException(
            "Class class __repr__ method has not been properly overwritten.")


class Property:
    def __init__(self, property_name, property_type):
        self.property_name = property_name
        self.property_type = property_type

    def __repr__(self):
        raise InterfaceException(
            "Property class __repr__ method has not been properly overwritten.")
        

class Method:
    def __init__(self, name, code):
        self.name = name
        self.code = code
        self.parameters = {}

    def add_parameter(self, param_name, param_object):
        self.parameters[param_name] = param_object

    def __repr__(self):
        raise InterfaceException(
            "Method class __repr__ method has not been properly overwritten.")

class Parameter:
    def __init__(self, param_name, param_type):
        self.param_name = param_name
        self.param_type = param_type
