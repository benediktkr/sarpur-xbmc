#!/usr/bin/env python
# encoding: UTF-8

import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime


def strptime(date_string, format):
    try:
        return datetime.strptime(date_string, format)
    except TypeError:
        # Bugfix for bug that doesn't make sense
        # http://forum.kodi.tv/showthread.php?tid=112916
        return datetime(*(time.strptime(date_string, format)[0:6]))

def get_document(url):
    """
    Downloads url and returns a BeautifulSoup object

    :param url: An url
    :return BeautifulSoup "document"
    """
    req = requests.get(url)
    doc = BeautifulSoup(req.content, "html.parser")
    return doc


def get_media_url(page_url):
    """
    Find the url to the MP4/MP3 on a page

    :param page_url: Page to find the url on
    :return: url
    """

    doc = get_document(page_url)
    sources = [tag['jw-src'] for tag in doc.find_all('source') if tag.has_attr('jw-src')]
    if len(sources) == 0:
        return -1

    return u"http://smooth.ruv.cache.is/{0}".format(sources[0][4:])


def get_podcast_shows(url):
    """
    Gets the names and rss urls of all the podcasts (shows)

    :param url: The url to the podcast index
    :return A list of 2-tuples with show name and rss url

    """
    doc = get_document(url)

    #doc = BeautifulSoup(file('/home/dagur/PycharmProjects/sarpur-xbmc/plugin.video.sarpur/hladvarp.htm'), "html.parser")

    return (
        {
            'img': show.find("img", title=u"Mynd með færslu")['srcset'],
            # 'show_url': show.find("strong").a['href'],
            'name': show.find("strong").a.text,
            'url': show.find_next_sibling().find("a", class_="button pad0 pad1t")['href']
        }
        for show in doc.find_all("div", class_="views-field views-field-nothing")
    )


def get_podcast_episodes(url):
    """
    Gets the items from the rss feed

    :param url: Get all the playable items in podcast rss
    :return a list of 2-tuples with airdate and media url

    """
    def parse_pubdate(date_string):
        date = None
        try:
            return strptime(date_string, '%a, %d %b %Y %H:%M:%S +0000')
        except ValueError:
            pass

        try:
            return strptime(date_string, '%a, %d %b %Y')
        except ValueError:
            pass

        try:
            return strptime(date_string, '%a, %d %b %Y%H:%M:%S +0000')
        except ValueError:
            pass

        try:
            return strptime(date_string, '%a, %d %b %Y %H:%M')
        except ValueError:
            pass

        try:
            return strptime(date_string, '%a, %d %b %Y %H.%M')
        except ValueError:
            pass

        return datetime.fromtimestamp(0)

    doc = get_document(url)

    return (
        {
            'url': item.select('guid')[0].text,
            'Premiered': parse_pubdate(item.select('pubdate')[0].text.decode('iso-8859-1')).strftime("%d.%m.%Y"),
            'Duration': item.find('itunes:duration').text.split(':')[0],
            'title': item.title.text,
            'Plot': item.description.text
        }
        for item in doc.find_all("item")
    )
