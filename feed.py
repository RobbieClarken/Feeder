from xml.etree import ElementTree as ET
from xml.dom import minidom
import copy

class Element(ET.Element):
    def __init__(self, *args, **kwargs):
        super(Element, self).__init__(*args, **kwargs)
        self.subelement_names = []
    def tostring(self):
        rough_string = ET.tostring(self.tree(), 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent='  ', encoding='utf-8')
    def tree(self):
        el = copy.copy(self)
        for subelement_name in self.subelement_names:
            if subelement_name in dir(self):
                subelement = self.__getattribute__(subelement_name)
                if subelement is None:
                    break
                if isinstance(subelement, list):
                    for subelement_item in subelement:
                        el.extend([subelement_item.tree()])
                else:
                    el.extend([subelement.tree()])
        return el

class Person(Element):
    def __init__(self, tag, name, email=None, uri=None, **kwargs):
        super(Person, self).__init__(tag, **kwargs)
        self.subelement_names = ['name', 'email', 'uri']
        # Required
        self.name = Element('name')
        self.name.text = name
        # Optional
        if email is not None:
            self.email = Element('email')
            self.email.text = email
        if uri is not None:
            self.uri = Element('uri')
            self.uri.text = uri

class Author(Person):
    def __init__(self, name, email=None, uri=None, **kwargs):
        super(Author, self).__init__('author', name, email, uri, **kwargs)

class Feed(Element):
    def __init__(self, id, title, updated=None):
        super(Feed, self).__init__('feed', {'xlmns': 'http://www.w3.org/2005/Atom'})
        self.subelement_names = [
            'id',
            'title',
            'updated',
            'authors',
            'link',
            'categories',
            'contributors',
            'generator',
            'icon',
            'logo',
            'rights',
            'subtitle'
        ]
        # Required
        self.id = Element('id')
        self.id.text = id
        self.title = Element('title')
        self.title.text = title
        self.updated = Element('updated')
        self.updated.text = updated.isoformat()
        # Recommended
        self.authors = [] # List of Person objects
        self.link = None
        # Optional
        self.categories = [] # List of Person objects
        self.contributors = [] # List of Category objects
        self.generator = None
        self.icon = None
        self.logo = None
        self.rights = None
        self.subtitle = None
