"""
A Python library for generating Atom feeds for podcasts.
Uses the specification described at
http://www.atomenabled.org/developers/syndication/
"""

from xml.etree import ElementTree as ET
from xml.dom import minidom
import copy
from datetime import datetime, timedelta
from uuid import UUID


def parse_datetime(dt):
    """Return RFC 3339 compliant datetime."""
    return dt.isoformat() + 'Z' if hasattr(dt, 'isoformat') else dt


def parse_timedelta(td):
    """Return time offset as HH:MM:SS.sss."""
    if isinstance(td, timedelta):
        microseconds_per_millisecond = 1000
        seconds_per_minute = 60
        minutes_per_hour = 60
        seconds_per_hour = seconds_per_minute * minutes_per_hour
        hours_per_day = 24
        hours = int(td.seconds / seconds_per_hour) + hours_per_day * td.days
        minutes = int(td.seconds / seconds_per_minute) % minutes_per_hour
        seconds = td.seconds % seconds_per_minute
        milliseconds = int(td.microseconds / microseconds_per_millisecond)
        return '%02i:%02i:%02i.%03i' % (hours, minutes, seconds, milliseconds)
    else:
        return td


def parse_id(id):
    """If id is a UUID, prefix it with "urn:uuid:"."""
    if isinstance(id, UUID):
        return 'urn:uuid:%s' % id
    else:
        return id


class Element(ET.Element):
    """Base class of all elements which are added to the feed."""
    def __init__(self, *args, **kwargs):
        for kw, kwval in kwargs.items():
            if kwval is None:
                del(kwargs[kw])
        super(Element, self).__init__(*args, **kwargs)
        self.subelement_names = []

    def tostring(self, pretty=False):
        rough_string = ET.tostring(self.tree(), 'utf-8')
        if not pretty:
            return '<?xml version="1.0" encoding="utf-8"?>' + rough_string
        else:
            reparsed = minidom.parseString(rough_string)
            return reparsed.toprettyxml(indent='  ', encoding='utf-8')

    def tree(self):
        el = copy.copy(self)
        for subelement_name in self.subelement_names:
            if subelement_name in dir(self):
                subelement = self.__getattribute__(subelement_name)
                if subelement is None:
                    continue
                if isinstance(subelement, ElementList):
                    el.extend(subelement.tree())
                elif isinstance(subelement, list):
                    for subelement_item in subelement:
                        if subelement_item is None:
                            continue
                        el.extend([subelement_item.tree()])
                else:
                    el.extend([subelement.tree()])
        return el

    def add_custom_element(self, tag, content=None, **kwargs):
        el = Element(tag, **kwargs)
        if content is not None:
            el.text = content
        self.__setattr__(tag, el)
        self.subelement_names.append(tag)


class ElementList(list):
    """A list of elements. Intended for subclassing to overwrite tree method."""
    def __init__(self, values=None):
        if values is None:
            values = []
        super(ElementList, self).__init__()
        for value in values:
            self.append(value)

    def tree(self):
        return self.tree_elements()

    def tree_elements(self):
        return [el.tree() for el in self]


class Person(Element):
    """
    <author> and <contributor> describe a person, corporation, or
    similar entity. It has one required element, name, and two optional
    elements: uri, email.
    * name: conveys a human-readable name for the person.
    * uri: contains a home page for the person.
    * email: contains an email address for the person.
    """
    def __init__(self, tag, name, email=None, uri=None):
        super(Person, self).__init__(tag)
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
    """Creates a <author> element. See Person class for more information."""
    def __init__(self, name, email=None, uri=None):
        super(Author, self).__init__('author', name, email, uri)


class Contributor(Person):
    """Creates a <contributor> element. See Person class for more information."""
    def __init__(self, name, email=None, uri=None):
        super(Contributor, self).__init__('contributor', name, email, uri)


class Link(Element):
    """
    Creates a <link> element to a web page or resource. Has one required
    attribute, href, and five optional attributes: rel, type, hreflang,
    title, and length.
    Required:
    * href: the URI of the referenced resource (typically a Web page)
    Optional:
    * rel: a single link relationship type. It can be a full URI (see
        extensibility), or one of the following predefined values
        (default=alternate):
        - alternate: an alternate representation of the entry or feed,
        for example a permalink to the html version of the entry, or
        the front page of the weblog.
        - enclosure: a related resource which is potentially large in
        size and might require special handling, for example an audio
        or video recording.
        - related: an document related to the entry or feed.
        - self: the feed itself.
        - via: the source of the information provided in the entry.
        - type indicates the media type of the resource.
    * type: the media type of the resource.
    * hreflang: the language of the referenced resource.
    * title: human readable information about the link, typically for
        display purposes.
    * length: the length of the resource, in bytes.
    """
    def __init__(self, href, rel=None, type=None, hreflang=None,
                 title=None, length=None):
        super(Link, self).__init__('link', href=href, rel=rel, type=type,
                                   hreflang=hreflang, title=title,
                                   length=length)


class Category(Element):
    """
    Creates a <category> element. Has one required attribute, term, and
    two optional attributes, scheme and label.
    Required:
    * term: identifies the category.
    Optional:
    * scheme: identifies the categorization scheme via a URI.
    * label: provides a human-readable label for display.
    """
    def __init__(self, term, scheme=None, label=None):
        super(Category, self).__init__('category', term=term,
                                       scheme=scheme, label=label)


class Chapter(Element):
    """
    Podcast chapters as described at http://podlove.org/simple-chapters/
    Required:
    * start: a single point in time relative to the beginning of the
      media file.
    * title: the name of the chapter.
    Optional:
    * href: a hypertext reference as an extension of the title that
      refers to a resource that provides related information.
    * image: an URL pointing to an image to be associated with the
      chapter.
    """
    def __init__(self, start, title, href=None, image=None):
        start = parse_timedelta(start)
        super(Chapter, self).__init__('psc:chapter', start=start,
                                      title=title, href=href,
                                      image=image)


class ChapterList(ElementList):
    """Chapters should be encapsulated in this class."""
    def __init__(self, values=None):
        if values is None:
            values = []
        super(ChapterList, self).__init__(values)

    def tree(self):
        if len(self) == 0:
            return []
        el = Element('psc:chapters', version="1.1")
        el.set('xmlns:psc', 'http://podlove.org/simple-chapters')
        el.extend(self.tree_elements())
        return [el]


class Entry(Element):
    """Generates an entry element to be added to the elements array
       in the Feed class.
       Required:
       * id: Identifies the entry using a universally unique and
         permanent URI. Two entries in a feed can have the same value
         for id if they represent the same entry at different points
         in time.
       * title: Contains a human readable title for the entry. This
         value should not be blank.
       * updated: Indicates the last time the entry was modified in a
         significant way. This value need not change after a typo is
         fixed, only after a substantial modification. Generally,
         different entries in a feed will have different updated
         timestamps.
       Recommended:
       * author: Names one author of the entry. An entry may have
         multiple authors. An entry must contain at least one author
         element unless there is an author element in the enclosing
         feed, or there is an author element in the enclosed source
         element. See Author class.
       * content: Contains or links to the complete content of the
         entry. Content must be provided if there is no alternate link,
         and should be provided if there is no summary.
       * link: Identifies a related Web page. The type of relation is
         defined by the rel attribute. An entry is limited to one
         alternate per type and hreflang. An entry must contain an
         alternate link if there is no content element. See Link class.
       * summary: Conveys a short summary, abstract, or excerpt of the
         entry. Summary should be provided if there either is no content
         provided for the entry, or that content is not inline (i.e.,
         contains a src attribute), or if the content is encoded in
         base64.
       Optional:
       * category: Specifies a category that the entry belongs to. A
         entry may have multiple category elements. See Category class.
       * contributor: Names one contributor to the entry. An entry may
         have multiple contributor elements. See Contributor class.
       * published: Contains the time of the initial creation or first
         availability of the entry.
       * source: If an entry is copied from one feed into another feed,
         then the source feed's metadata (all child elements of feed
         other than the entry elements) should be preserved if the
         source feed contains any of the child elements author,
         contributor, rights, or category and those child elements are
         not present in the source entry.
       * rights: Conveys information about rights, e.g. copyrights, held
         in and over the entry.
       * chapters: Podcast chapters as described at
         http://podlove.org/simple-chapters/. See Chapter class.
    """
    def __init__(self, id, title, updated, authors=None, content=None,
                 links=None, summary=None, categories=None, contributors=None,
                 published=None, source=None, rights=None, chapters=None):
        if authors is None:
            authors = []
        if links is None:
            links = []
        if categories is None:
            categories = []
        if contributors is None:
            contributors = []
        if chapters is None:
            chapters = []
        super(Entry, self).__init__('entry')
        self.subelement_names = [
            'id',
            'title',
            'updated',
            'authors',
            'content',
            'links',
            'summary',
            'categories',
            'contributors',
            'published',
            'source',
            'rights',
            'chapters'
        ]
        self.id = Element('id')
        self.id.text = parse_id(id)
        self.title = Element('title')
        self.title.text = title
        self.updated = Element('updated')
        self.updated.text = parse_datetime(updated)
        self.authors = authors
        if content:
            self.content = Element('content')
            self.content.text = content
        self.links = links
        if summary:
            self.summary = Element('summary')
            self.summary.text = summary
        self.categories = categories
        self.contributors = contributors
        if published is not None:
            self.published = Element('published')
            self.published.text = parse_datetime(published)
        self.source = source  # Should be an Entry
        if rights:
            self.rights = Element('rights')
            self.rights.text = rights
        self.chapters = ChapterList(chapters)


class Feed(Element):
    """Generates an Atom feed based on the specification described at
       http://www.atomenabled.org/developers/syndication/
       Required elements:
       * id: Identifies the feed using a universally unique and
         permanent URI. If you have a long-term, renewable lease on
         your Internet domain name, then you can feel free to use
         your website's address.
       * title: Contains a human readable title for the feed. Often the
         same as the title of the associated website. This value should
         not be blank.
       * updated: Indicates the last time the feed was modified in a
         significant way.
       Recommended elements:
       * author: Names one author of the feed. A feed may have multiple
         author elements. A feed must contain at least one author
         element unless all of the entry elements contain at least one
         author element. See Author class.
       * link: Identifies a related Web page. The type of relation is
         defined by the rel attribute. A feed is limited to one
         alternate per type and hreflang. A feed should contain a link
         back to the feed itself. See Link class.
       Optional elements:
       * category: Specifies a category that the feed belongs to. A
         feed may have multiple category elements. See Category class.
       * contributor: Names one contributor to the feed. An feed may
         have multiple contributor elements.
       * generator: Identifies the software used to generate the feed,
         for debugging and other purposes. Both the uri and version
         attributes are optional.
       * icon: Identifies a small image which provides iconic visual
         identification for the feed. Icons should be square.
       * logo: Identifies a larger image which provides visual
         identification for the feed. Images should be twice as wide as
         they are tall.
       * rights: Conveys information about rights, e.g. copyrights, held
         in and over the feed.
       * subtitle: Contains a human-readable description or subtitle for
         the feed.
    """
    def __init__(self, id, title, updated=None, authors=None, links=None,
                 categories=None, contributors=None, generator=None,
                 icon=None, logo=None, rights=None, subtitle=None, entries=None,
                 **kwargs):
        if authors is None:
            authors = []
        if links is None:
            links = []
        if categories is None:
            categories = []
        if contributors is None:
            contributors = []
        if entries is None:
            entries = []
        if 'xmlns' not in kwargs:
            kwargs['xmlns'] = 'http://www.w3.org/2005/Atom'
        super(Feed, self).__init__('feed', **kwargs)
        if updated is None:
            updated = datetime.now()
        self.subelement_names = [
            'id',
            'title',
            'updated',
            'authors',
            'links',
            'categories',
            'contributors',
            'generator',
            'icon',
            'logo',
            'rights',
            'subtitle',
            'entries'
        ]
        # Required
        self.id = Element('id')
        self.id.text = parse_id(id)
        self.title = Element('title')
        self.title.text = title
        self.updated = Element('updated')
        self.updated.text = parse_datetime(updated)
        # Recommended
        self.authors = authors
        self.links = links
        # Optional
        self.categories = categories
        self.contributors = contributors  # List of Category objects
        if generator:
            self.generator = Element('generator')
            self.generator.text = generator
        if icon:
            self.icon = Element('icon')
            self.icon.text = icon
        if logo:
            self.logo = Element('logo')
            self.logo.text = logo
        if rights:
            self.rights = Element('rights')
            self.rights.text = rights
        if subtitle:
            self.subtitle = Element('subtitle')
            self.subtitle.text = subtitle
        self.entries = entries
