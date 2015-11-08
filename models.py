# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Boolean, Unicode, DateTime, UnicodeText, MetaData, ForeignKey
from sqlalchemy.orm import relation, backref
from sqlalchemy.ext.declarative import declarative_base

from bottle.ext import sqlalchemy
from bottle import install as bottle_install

from sqlalchemy import create_engine
# 設定ファイル読み込み用
import os.path
import yaml

print "models"


CONFIG_FILENAME = "config.yaml"

def get_conection_string():
    config_pass = os.path.join(os.path.dirname(__file__), CONFIG_FILENAME)
    if os.path.isfile(config_pass):
        with open(config_pass, 'r') as cf:
            conf_dic = yaml.load(cf)  # 読み込む
        if not isinstance(conf_dic, dict):
            conf_dic = {}
    else:
        conf_dic = {}

    username = conf_dic.get("username", "ougi")
    password = conf_dic.get("password", "ougi_reader0")
    hostname = conf_dic.get("hostname", "localhost")
    ip = conf_dic.get("ip", "3306")
    table = conf_dic.get("table", "ougi_reader")

    return "mysql://%s:%s@%s:%s/%s?charset=utf8" % (username, password, hostname, ip, table)


# 初期化処理
Base = declarative_base()

engine = create_engine(get_conection_string(), echo=False)

# bottle-sqlalchemyの設定
plugin = sqlalchemy.Plugin(
    engine,
    Base.metadata,
    keyword='db',  # 関数内で挿入される場合の変数名
    create=True,  # テーブルを作成するか
    commit=True,  # 関数終了時にコミットするか
    use_kwargs=False
)

# プラグインのインストール
bottle_install(plugin)


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

    feed = relation(Feed, backref=backref('entries', order_by=id),
        cascade="all, delete, delete-orphan", single_parent=True )

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


def add_feed(db, url, title=None):
    feed = Feed(
        url=url,
        title=title
    )
    # feedを保存
    db.add(feed)

    # idを使いたいので、ここでcommitしておく
    db.commit()

    return feed;

def get_entries(db, feed_id=None):
    entries = []
    if feed_id is None:
        entries = db.query(Entry).order_by("published_at").all()
    else:
        entries = db.query(Entry).filter(Entry.feed_id == feed_id).order_by("published_at").all()

    if entries is not None:
        return reversed(entries)
    else:
        return None

def get_feed(db, feed_id):
    return db.query(Feed).get(feed_id)

def get_all_feeds(db):
    return db.query(Feed).all()

def get_same_url_feed(db, feed_url):
    # 有無が知りたいので、先頭だけでよい(むしろ複数あるような状態がおかしい)
    feed = db.query(Feed).filter(Feed.url == feed_url).first()
    return feed
