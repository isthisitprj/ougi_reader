# -*- coding: utf-8 -*-

from datetime import datetime
import feedparser

from models import Entry

# 日付変換
def conv_structtime_to_datetime(struct_time):
    return datetime(*struct_time[:6])

# Entryのソート
def sorted_by_pubdate_in_des(entryList):
    return sorted(entryList, key=lambda entry: entry.published_at, reverse=True)


def get_date(feed):
    if hasattr(feed, 'published_parsed'):
        return conv_structtime_to_datetime(feed.published_parsed)
    elif hasattr(feed, 'updated_parsed'):
        return conv_structtime_to_datetime(feed.updated_parsed)
    else:
        return None

def checkNewEntries(newList, last_updated_at):
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
            description = e.description
        else:
            description = e.sammary
        entryList.append(Entry(e.title,  conv_structtime_to_datetime(e.published_parsed), feed_id, e.link, description))
    return entryList


def update_feeds(feeds, info=None):
    for feed in feeds:
        if info is None:
            info = feedparser.parse(feed.url)

        newEntries = update_entry(info, feed.id)
        if len(feed.entries) != 0:
            newEntries = checkNewEntries(sorted_by_pubdate_in_des(newEntries), feed.last_updated_at)
        feed.entries.extend(newEntries)

        feed.published_at = get_date(info.feed)
        feed.last_updated_at = datetime.now()


def setup_feed(feed):
    info = feedparser.parse(feed.url)
    feed_info = info.feed

    if not feed.title:
        # TODO titleの実態参照が2重がけになり、表示されるときに解消されない
        feed.title = feed_info.title

    update_feeds([feed], info)
