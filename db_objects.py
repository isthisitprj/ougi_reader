# -*- coding: utf-8 -*-

from sqlalchemy import create_engine, Column, Integer, String, Boolean, Unicode, DateTime, UnicodeText, MetaData, ForeignKey
from sqlalchemy.orm import relation, backref
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Feed(Base):
    # feedsテーブル
    __tablename__ = 'feeds'

    # カラムの定義
    id = Column(Integer, primary_key=True)
    title = Column(Unicode(100), nullable=False)
    url = Column(String(2000), nullable=False)
    last_updated_at = Column(DateTime)
    published_at = Column(DateTime)


    def __init__(self,  url, title=None, published_at=None, last_updated_at=None):
       self.title = title
       self.url = url
       self.published_at = published_at
       self.last_updated_at = last_updated_at

    def __repr__(self):
        return "<Feed('%s', '%s', '%s', '%s', '%d')>" % (
            self.title,
            self.url,
            self.published_at,
            self.last_updated_at,
            len(self.entries)
            )

class Entry(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    title = Column(Unicode(100), nullable=False)
    published_at = Column(DateTime)
    # ...
    feed_id = Column(Integer, ForeignKey('feeds.id'))

    read = Column(Boolean, default=False)
    read_at = Column(DateTime)
    url = Column(String(2000), nullable=False)
    description = Column(Unicode(2000))

    feed = relation(Feed, backref=backref('entries', order_by=id))

    def __init__(self, title, published_at, feed_id, url, description, read=False, read_at=None):
        self.title = title
        self.published_at = published_at
    # ...
        self.feed_id = feed_id

        self.read = read
        self.read_at = read_at
        self.url = url
        self.description = description

    def __repr__(self):
        return "<Entry('%s', '%s', '%d')>" % (self.title, self.url, self.feed_id)

engine = create_engine('mysql://mikan:kitoo@localhost:3306/ougi_test?charset=utf8', echo=False)
Base.metadata.create_all(engine)
