# -*- coding: utf-8 -*-

from datetime import datetime
import feedparser
from urllib2 import URLError

from models import Entry

# 日付変換
def _conv_structtime_to_datetime(struct_time):
    return datetime(*struct_time[:6])

# Entryのソート
def _sorted_by_pubdate_in_des(entryList):
    return sorted(entryList, key=lambda entry: entry.published_at, reverse=True)


def _get_info(url):
    info = feedparser.parse(url)
    if hasattr(info, "bozo_exception"):
        exc = info.bozo_exception
        if isinstance(exc, URLError):
            return None

    return info


def _get_feed_date(feed):
    if hasattr(feed, 'published_parsed'): # RSSのfeedの場合
        return _conv_structtime_to_datetime(feed.published_parsed)
    elif hasattr(feed, 'updated_parsed'): # Atomのfeedの場合
        return _conv_structtime_to_datetime(feed.updated_parsed)
    else:
        return None


def _check_new_entries(newList, last_updated_at):
    if last_updated_at is None:
        return newList

    entryList = []
    print "last_updaTed_at: " + str(last_updated_at)

    for e in newList:
        newEntryDate = e.published_at
        print "newEntryDate: " + str(newEntryDate)
        print newEntryDate > last_updated_at
        if newEntryDate > last_updated_at:
            continue
        elif newEntryDate == last_updated_at:
            # TODO 後で頑張る
            continue
        else:
            print "index: %d" % newList.index(e)
            entryList = newList[:newList.index(e)]
            print "break"
            break

    return entryList


def update_entry(info, feed_id):
    entryList = []
    for e in info.entries:
        if e.description is not None:
            description = e.description[:200]
        else:
            description = e.sammary
        entryList.append(Entry(e.title,  _conv_structtime_to_datetime(e.published_parsed), feed_id, e.link, description))
    return entryList


def update_feed(feed, info=None):
    if info is None:
        info = _get_info(feed.url)
        if info is None:
            return

    newEntries = update_entry(info, feed.id)
    if len(feed.entries) != 0:
        newEntries = _check_new_entries(_sorted_by_pubdate_in_des(newEntries), feed.last_updated_at)
    feed.entries.extend(newEntries)

    feed.published_at = _get_feed_date(info.feed)
    feed.last_updated_at = datetime.now()


def update_feeds(feeds_list):
    for feed in feeds_list:
        info = _get_info(feed.url)
        if info is None:
            break
        update_feed(feed, info)


def setup_feed(feed):
    info = _get_info(feed.url)
    if info is None:
        return None

    if not feed.title:
        # TODO titleの実態参照が2重がけになり、表示されるときに解消されない
        feed.title = info.feed.title

    update_feed(feed, info)
    return feed
