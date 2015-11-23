# -*- coding: utf-8 -*-


import math

import models


ENTRIES_PER_PAGE = 20


def get_shwon_entries(entries, shown_page):
    if entries:
        entries_length = len(entries)
        last_page = int(math.ceil(float(entries_length) / ENTRIES_PER_PAGE))
        # 表示するページが、最後のページより後ろの場合は、最後のページを表示する
        if last_page < shown_page:
            shown_page = last_page
        if shown_page < 1:
            shown_page = 1
        first_index = (shown_page - 1) * ENTRIES_PER_PAGE
        last_index = shown_page * ENTRIES_PER_PAGE

        print "entries_length:%d, last_page:%d, first: %d, last: %d" %\
                (len(entries), last_page, first_index, last_index)

        if last_index < entries_length:
            entries = entries[first_index:last_index]
        elif first_index < entries_length:
            entries = entries[first_index:]
        return entries, shown_page, entries_length
    else:
        return entries, 0, 0
