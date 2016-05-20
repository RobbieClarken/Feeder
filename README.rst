Feeder
======

Feeder is a python module for producing Atom podcast feeds.


Installation
------------

.. code-block:: bash

    pip install git+https://github.com/RobbieClarken/Feeder


Usage
-----

.. code-block:: python

    from feeder import Feed, Author, Category, Link, Entry
    from datetime import datetime

    feed = Feed(id='http://example.com',
                       title='Example Feed',
                       authors=[Author('Jack Black')],
                       logo='http://example.com/logo.jpg',
                       categories=[Category('Technology'),
                                   Category('Society & Culture')])
    feed.set('xml:lang', 'en')
    feed.links = [
      Link('http://example.com/'),
      Link('http://example.com/feed.xml', rel='self')
    ]
    feed.entries.append(Entry(id='http://example.com/ep_123.mp3',
                              title='Episode 123',
                              updated=datetime.now(),
                              links=[Link('http://example.com/ep_123.mp3',
                                           rel="enclosure", type="audio/mpeg")]))
    print(feed.tostring(pretty=True))


Output:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <feed xml:lang="en" xmlns="http://www.w3.org/2005/Atom">
      <id>http://example.com</id>
      <title>Example Feed</title>
      <updated>2013-02-21T13:34:07.480337Z</updated>
      <author>
        <name>Jack Black</name>
      </author>
      <link href="http://example.com/"/>
      <link href="http://example.com/feed.xml" rel="self"/>
      <category term="Technology"/>
      <category term="Society &amp; Culture"/>
      <logo>http://example.com/logo.jpg</logo>
      <entry>
        <id>http://example.com/ep_123.mp3</id>
        <title>Episode 123</title>
        <updated>2013-02-21T13:34:07.495327Z</updated>
        <link href="http://example.com/ep_123.mp3" rel="enclosure" type="audio/mpeg"/>
      </entry>
    </feed>
