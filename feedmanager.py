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

# TODO
def _get_info_from_attr(url):
    return None

def _get_info_and_url(url):

    info = feedparser.parse(url)
    if not hasattr(info, "bozo_exception"):
        return (info, url)

    exc = info.bozo_exception
    # if isinstance(exc, URLError):
    #    return None
    # return None

    # 与えられたurlがページ自体のものだとみなし、feedurlを取得を試みる

    # htmlのlink属性からのfeedurlを取得を試みる
    url_from_attr = _get_info_from_attr(url)
    info = feedparser.parse(url_from_attr)
    if not hasattr(info, "bozo_exception"):
        return (info, url_from_attr)

    exc = info.bozo_exception

    # urlによくあるパターンを当てはめてfeedurlを取得を試みる
    if url.endswith("/"):
        url = url[:-1]

    feed_suffixes = ["/feed", ".atom", "/?mode=atom"]
    url_from_patterns = map(lambda sfx:url + sfx, feed_suffixes)
    for url_from_pattern in url_from_patterns:
        info = feedparser.parse(url_from_pattern)
        if not hasattr(info, "bozo_exception"):
            return (info, url_from_pattern)

    # feedが取得できなかった
    return None


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
        if newEntryDate > last_updated_at:
            continue
        elif newEntryDate == last_updated_at:
            # TODO 後で頑張る？
            continue
        else:
            print "* get %d new entries" % newList.index(e)
            entryList = newList[:newList.index(e)]
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
        info_and_url = _get_info_and_url(feed.url)
        if info_and_url is None:
            return [u"%s(%d)を取得できませんでした。" % (feed.title, feed.id)]

        info = info_and_url[0]
        feed.url = info_and_url[1]


    newEntries = update_entry(info, feed.id)
    if len(feed.entries) != 0:
        newEntries = _check_new_entries(_sorted_by_pubdate_in_des(newEntries), feed.last_updated_at)
    feed.entries.extend(newEntries)

    feed.published_at = _get_feed_date(info.feed)
    feed.last_updated_at = datetime.now()


def update_feeds(feeds_list):
    errors = []
    for feed in feeds_list:
        info_and_url = _get_info_and_url(feed.url)
        if info_and_url is None:
            # update_feedにNoneを渡しても、中でよしなにしてくれるけど、
            # 重たい処理なのでこっちでbreakする
            errors.append(u"%s(%d)の記事を取得できませんでした。" % (feed.title, feed.id))
            break
        info = info_and_url[0]
        feed.url = info_and_url[1]
        update_feed(feed, info)
    return errors


def setup_feed(feed):
    info_and_url = _get_info_and_url(feed.url)
    if info_and_url is None:
        return None
    else:
        info = info_and_url[0]
        feed.url = info_and_url[1]

    if not feed.title:
        # TODO titleの実態参照が2重がけになり、表示されるときに解消されない
        feed.title = info.feed.title

    return feed
