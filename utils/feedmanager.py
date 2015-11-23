# -*- coding: utf-8 -*-

"""feedmanager - treat feeds and its entries.

* create feeds and entries
* update entries of feeds
* check and find feeds URL
"""

from datetime import datetime
# from urllib2 import URLError

import feedparser

from models import Entry

# when entry doesn't have sammary
MAX_DESCRIPTION_LENGTH = 500

MAX_SAMMARY_LENGTH = 2000


def _conv_structtime_to_datetime(struct_time):
    """convert struct_time to datetime (second precision) for storing in DB."""
    # struct_time[5] is second
    return datetime(*struct_time[:6])


def _sorted_by_pubdate_in_des(entryList):
    """sort entries list by published_at in descending order.

    :rtype:     list of entries
    :return:    sorted list
    """
    return sorted(entryList, key=lambda entry: entry.published_at,
                  reverse=True)


def _get_info_from_attr(url):
    """*not yet impl* get feed info by searching feed URL in html.

    :rtype:     String
    :return:    feed URL

    Usually, feed URL is described in link tag
    with 'rel="alternate" type="application/rss+xml"' or
    'rel="alternate" type="application/atom+xml"'.
    And sometimes there are several feed URL.
    """
    # TODO
    return None


def _get_info_and_url(url, etag=None):
    """get feed info and URL in taple (info, url).

    :rtype:     (info, url)
    :return:    feed info and feed URL

    use several below strategy for getting feed URL.
    * use plain param
    * *not yet impl* search link tag in html rerurned by plain param
    * try some patterns URL suffixes
    """
    if etag is None:
        info = feedparser.parse(url)
    else:
        info = feedparser.parse(url, etag=etag)
    if "bozo_exception" not in info:
        return (info, url)

    # exc = info.bozo_exception
    # 本当は、エラーの種類ごとに細かくチェックしたいが、、、
    # if isinstance(exc, URLError):
    #    return None
    # return None

    # 与えられたurlがページ自体のものだとみなし、feedurlを取得を試みる

    # htmlのlink属性からのfeedurlを取得を試みる
    url_from_attr = _get_info_from_attr(url)
    info = feedparser.parse(url_from_attr)
    if "bozo_exception" not in info:
        return (info, url_from_attr)

    # exc = info.bozo_exception

    # urlによくあるパターンを当てはめてfeedurlを取得を試みる
    if url.endswith("/"):
        url = url[:-1]

    feed_suffixes = ["/feed", ".atom", "/?mode=atom"]
    for suffix in feed_suffixes:
        url_from_pattern = url + suffix
        info = feedparser.parse(url_from_pattern)
        if "bozo_exception" not in info:
            return (info, url_from_pattern)

    # feedが取得できなかった
    return None


def _get_published_date(something_info):
    """get date as published_at from info.feed or info.entries[i].

    :rtype:     datetime
    :return:    date as feed.published_at or entiy.published_at

    If something_info is RSS feed, it hasn't updated_parsed.
    So return published_parsed.
    And if something_info is Atom feed, it hasn't published_parsed.
    So returnupdated_parsed.
    """
    if "published_parsed" in something_info:  # RSSのfeedの場合
        return _conv_structtime_to_datetime(something_info.published_parsed)
    elif "updated_parsed" in something_info:  # Atomのfeedの場合
        return _conv_structtime_to_datetime(something_info.updated_parsed)
    else:
        return None


def _filter_new_entries(newList, last_updated_at):
    """filter out already geted entries from param.

    :rtype:     entry list
    :return:    list or entries added after this module updated last
    """
    if last_updated_at is None:
        return newList

    entryList = []
    # print "last_updaTed_at: " + str(last_updated_at)

    for e in newList:
        newEntryDate = e.published_at
        # print "newEntryDate: " + str(newEntryDate)
        if newEntryDate > last_updated_at:
            continue
        elif newEntryDate == last_updated_at:
            # TODO 後で頑張る？
            continue
        else:
            # print "* get %d new entries" % newList.index(e)
            entryList = newList[:newList.index(e)]
            break

    return entryList


def _get_now_entries(info, feed_id):
    """create new entries from feed info.

    :rtype:     entry list
    :return:    list or all entries published now
    """
    entryList = []
    for e in info.entries:
        # descriptionがあるならRSS、ないならAtom
        if e.description is not None:
            description = e.description
            if MAX_DESCRIPTION_LENGTH < len(description):
                description = description[:MAX_DESCRIPTION_LENGTH] + u"…"
        else:
            description = e.sammary
            if MAX_SAMMARY_LENGTH < len(description):
                description = description[:MAX_SAMMARY_LENGTH] + u"…"
        entryList.append(Entry(e.title, _get_published_date(e), feed_id,
                               e.link, description))
    return entryList


def _make_old_entries_read(feed):
    feed.unread_num = 0
    entries = reversed(feed.entries)
    for entry in entries:
        if not entry.read:
            entry.read = True
        else:
            break


def update_feed(feed, info=None):
    """add new feed's entries and update published_at and last_updated_at.

    :rtype:     error list
    :return:    list of error occured in updating
    """
    # 既読処理(暫定)
    _make_old_entries_read(feed)

    if info is None:
        info_and_url = _get_info_and_url(feed.url, etag=feed.etag)
        if info_and_url is None:
            return [u"%s(%d)を取得できませんでした。" % (feed.title, feed.id)]

        info = info_and_url[0]
        feed.url = info_and_url[1]
        if "etag" in info:
            feed.etag = info.etag


    newEntries = _get_now_entries(info, feed.id)
    if feed.entries:
        newEntries = _filter_new_entries(
            _sorted_by_pubdate_in_des(newEntries), feed.last_updated_at)

    feed.unread_num += len(newEntries)
    feed.entries.extend(newEntries)

    feed.published_at = _get_published_date(info.feed)
    feed.last_updated_at = datetime.now()


def update_feeds(feeds_list):
    """update several feeds.

    :rtype:     error list
    :return:    list of error occured in updating
    """
    errors = []
    for feed in feeds_list:
        info_and_url = _get_info_and_url(feed.url)
        if info_and_url is None:
            # update_feedにNoneを渡しても、中でよしなにしてくれるけど、
            # 重たい処理なのでこっちでbreakする
            errors.append(u"%s(%d)の記事を取得できませんでした。" % (feed.title, feed.id))
            # 既読処理(暫定)
            _make_old_entries_read(feed)
            continue
        info = info_and_url[0]
        feed.url = info_and_url[1]
        if "etag" in info:
            feed.etag = info.etag
        update_feed(feed, info)
    return errors


def setup_feed(feed):
    """validate feed URL and title.

    :rtype:     Feed or None
    :return:    Feed validated its URL or None

    If given feed URL is invalid, try getting feed URL by several stategy.
    If given feed title is None, try getting in feed info.
    """
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
