from xml.etree import ElementTree as ET
from xml.dom import minidom
import copy
from datetime import datetime

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

class Contributor(Person):
    def __init__(self, name, email=None, uri=None, **kwargs):
        super(Contributor, self).__init__('contributor', name, email, uri, **kwargs)

class Link(Element):
    """<link> is patterned after html's link element. It has one
       required attribute, href, and five optional attributes: rel,
       type, hreflang, title, and length.
       * href is the URI of the referenced resource (typically a Web
         page)
       * rel contains a single link relationship type. It can be a full
         URI (see extensibility), or one of the following predefined
         values (default=alternate):
         - alternate: an alternate representation of the entry or feed,
           for example a permalink to the html version of the entry, or
           the front page of the weblog.
         - enclosure: a related resource which is potentially large in
           size and might require special handling, for example an audio
           or video recording.
         - related: an document related to the entry or feed.
         - self: the feed itself.
         - via: the source of the information provided in the
           entry.
         - type indicates the media type of the resource.
       * hreflang indicates the language of the referenced resource.
       * title human readable information about the link, typically for
         display purposes.
       * length the length of the resource, in bytes.
    """
    def __init__(self, href, **kwargs):
        super(Link, self).__init__('link', href=href, **kwargs)

class Feed(Element):
    def __init__(self, id, title, updated=None):
        #TODO: kwargs to be appended to super initialisation
        super(Feed, self).__init__('feed', {'xlmns': 'http://www.w3.org/2005/Atom'})
        if updated is None:
            updated = datetime.now()
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

