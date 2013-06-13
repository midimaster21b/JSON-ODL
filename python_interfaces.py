from interfaces import Class, Method, Property


class Python_Class(Class):
    def __init__(self, name):
        # super...
        pass

    def __repr__(self):
        retval = ("class {class_name}:\n" + 4 * ' ').format(class_name=self.name)
        for method in self.methods:
            method += "\n"
            retval += method.replace('\n', '\n' + 4 * ' ')

        return retval +  "\n"


class Python_Method(Method):
    def __init__(self, name, code):
        # super...
        pass

    def __repr__(self):
        return 'def {0}({1}):\n{2}'.format(
            self.name,
            ', '.join([param for param in self.parameters]),
            self.code)


class Python_Property(Property):
    def __init__(self, property_name, property_type):
        # super...
        pass

    def __repr__(self):
        return self.property_name
