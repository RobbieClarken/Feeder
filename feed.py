from xml.etree import ElementTree as ET
import copy

class Element(ET.Element):
    def __init__(self, *args, **kwargs):
        super(Element, self).__init__(*args, **kwargs)
        self.subelement_names = []
    def tostring(self):
        return ET.tostring(self.tree())
    def tree(self):
        el = copy.copy(self)
        for subelement_name in self.subelement_names:
            if subelement_name in dir(self):
                el.extend([self.__getattribute__(subelement_name).tree()])
        return el

class Person(Element):
    def __init__(self, tag, name, email=None, uri=None, **kwargs):
        super(Person, self).__init__(tag, **kwargs)
        self.subelement_names = ['name', 'email', 'uri']
        # Required
        self.name = Element('name')
        self.name.text = name
        if email is not None:
            self.email = Element('email')
            self.email.text = email
        if uri is not None:
            self.uri = Element('uri')
            self.uri.text = uri
