# -*- coding: utf-8 -*-

from datetime import datetime

import bottle
from bottle import get, post, run, view
from bottle import request, template, redirect
from bottle import HTTPError

from sqlalchemy import create_engine, Column, Integer, String, Boolean, Unicode, DateTime, UnicodeText, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, backref

from bottle.ext import sqlalchemy

from wtforms.form import Form
from wtforms import validators
from wtforms import StringField, IntegerField, TextAreaField

import db_objects.py

Base = declarative_base()
#engine = create_engine('sqlite:///:memory:', echo=True)
engine = create_engine('mysql://ougi:ougi_reader0@localhost:3306/ougi_reader?charset=utf8', echo=False)
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
bottle.install(plugin)

class Feed(Base):
    # feedsテーブル
    __tablename__ = 'feeds'

    # カラムの定義
    id = Column(Integer, primary_key=True)
    title = Column(Unicode(100))
    url = Column(String(2000), nullable=False)
    last_updated_at = Column(DateTime, default=None)
    published_at = Column(DateTime, default=None)

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
    read_at = Column(DateTime, default=None)
    url = Column(String(2000), nullable=False)
    description = Column(Unicode(2000))

    feed = relation(Feed, backref=backref('entries', order_by=id))

    def __repr__(self):
        return "<Entry('%s', '%s', '%d')>" % (self.title, self.url, self.feed_id)


class FeedForm(Form):
    title = StringField(u'タイトル', [
        validators.required(message=u"入力してください"),
        validators.length(min=1, max=100, message=u"100文字以下で入力してください")
    ])
    url = StringField(u'url', [
        validators.required(message=u"入力してください"),
        validators.length(min=1, max=2000, message=u"2000文字以下で入力してください")
    ])


@get('/')
def index(db):
    # feedsテーブルから全件取得
    entries = db.query(Entry).order_by("published_at").all()

    # index.tplの描画
    return template('index', entries=reversed(entries), request=request)


@get('/add')
def new(db):
    form = FeedForm()

    # add.tplの描画
    return template('add', form=form, request=request)


@post('/add')
def create(db):
    form = FeedForm(request.forms.decode())

    # フォームのバリデーション
    if form.validate():

        # Feedインスタンスの作成
        feed = Feed(
            title=form.title.data,
            url=form.url.data,
        )

        # feedを保存
        db.add(feed)

        # 一覧画面へリダイレクト
        # TODO 自分の一覧にリダイレクト
        redirect("./")
    else:
        return template('add', form=form, request=request)

@get('/<id:int>')
def edit(db, id):
    # Feedの検索
    feed = db.query(Feed).get(id)
    # Feedが存在しない(404を表示）
    if not feed:
        return HTTPError(404, 'Feed is not found.')

    entries = db.query(Entry).filter(Entry.feed_id == id).order_by("published_at").all()

    # index.tplの描画
    return template('index', entries=reversed(entries), request=request)


@get('/<id:int>/edit')
def edit(db, id):
    # Feedの検索
    feed = db.query(Feed).get(id)

    # Feedが存在しない(404を表示）
    if not feed:
        return HTTPError(404, 'Feed is not found.')

    # フォームを作成
    form = FeedForm(request.POST, feed)

    # edit.tplを描画
    return template('edit', feed=feed, form=form, request=request)


@post('/<id:int>/edit')
def update(db, id):
    # Feedの検索
    feed = db.query(Feed).get(id)

    # Feedが存在しない(404を表示）
    if not feed:
        return HTTPError(404, 'Feed is not found.')

    form = FeedForm(request.forms.decode())

    if form.validate():
        # feed情報を更新
        feed.title = form.title.data
        feed.url = form.url.data

        # 一覧画面へリダイレクト
        # TODO 自分の一覧にリダイレクト
        redirect("../")
    else:
        return template('edit', form=form, request=request)


@post('/<id:int>/delete')
def destroy(db, id):
    # Feedの検索
    feed = db.query(Feed).get(id)

    # Feedが存在しない(404を表示）
    if not feed:
        return HTTPError(404, 'Feed is not found.')

    # feedを削除
    db.delete(feed)

    # 一覧画面へリダイレクト
    redirect("../")


if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True, reloader=True)
