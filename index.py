# -*- coding: utf-8 -*-

import bottle
from bottle import get, post, run, view
from bottle import request, template, redirect
from bottle import HTTPError

from sqlalchemy import create_engine

from bottle.ext import sqlalchemy

from wtforms.form import Form
from wtforms import validators
from wtforms import StringField, IntegerField, TextAreaField

import models
import feedmanager


Base = models.Base
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


class FeedForm(Form):
    title = StringField(u'タイトル', [
        validators.Optional(),
        validators.length(min=1, max=100, message=u"100文字以下で入力してください")
    ])
    url = StringField(u'URL', [
        validators.InputRequired(message=u"入力してください"),
        validators.length(min=1, max=2000, message=u"2000文字以下で入力してください")
    ])


@get('/')
def index(db):

    # feedの更新
    feeds = models.get_all_feeds(db)
    errors = feedmanager.update_feeds(feeds)

    # entriesテーブルから全件取得
    entries = models.get_entries(db)

    # index.tplの描画
    return template('index', title=None, entries=entries, errors=error, request=request)


@get('/add')
def new(db):
    form = FeedForm()

    # add.tplの描画
    return template('add', form=form, request=request)


@post('/add')
def create(db):
    form = FeedForm(request.forms.decode())

    # フォームのバリデーション
    if not form.validate():
        return template('add', form=form, request=request)

    # Feedの生成と格納
    feed = models.add_feed(db,
        title=form.title.data,
        url=form.url.data,
    )

    feed = feedmanager.setup_feed(feed)

    if feed is None:
        form.url.errors.append(u"URLからフィードを取得できませんでした。")
        return template('add', form=form, request=request)


    # feedを既存から検索し、重複していればエラー扱い&コミットしない
    same_url_feed = models.get_same_url_feed(db, feed.url)

    if same_url_feed is not None:
        form.url.errors.append(
            u"すでに同じフィードが登録されています。(「%s」)" % feed.title)
        # insertしてしまっているので、元に戻す(1行だけなので、modelsにはとりあえず入れないでおく)
        db.delete(feed)
        return template('add', form=form, request=request)


    # 該当フィードの記事の一覧画面へリダイレクト(リダイレクト先で更新処理が行われる)
    redirect("./" + str(feed.id))


@get('/<feed_id:int>')
def edit(db, feed_id):
    # Feedの検索
    feed = models.get_feed(db, feed_id)
    # Feedが存在しない(404を表示）
    if not feed:
        return HTTPError(404, 'Feed is not found.')

    # feedの更新
    errors = feedmanager.update_feed(feed)
    entries = models.get_entries(db, feed_id)

    # index.tplの描画
    return template('index', title=feed.title, entries=entries, errors=error, request=request)


@get('/<feed_id:int>/edit')
def edit(db, feed_id):
    # Feedの検索
    feed = models.get_feed(db, feed_id)

    # Feedが存在しない(404を表示）
    if not feed:
        return HTTPError(404, 'Feed is not found.')

    # フォームを作成
    form = FeedForm(request.POST, feed)

    # edit.tplを描画
    return template('edit', feed=feed, form=form, request=request)


@post('/<feed_id:int>/edit')
def update(db, feed_id):
    # Feedの検索
    feed = models.get_feed(db, feed_id)

    # Feedが存在しない(404を表示）
    if not feed:
        return HTTPError(404, 'Feed is not found.')

    form = FeedForm(request.forms.decode())

    if not form.validate():
        return template('edit', form=form, request=request)

    # feed情報を更新
    feed.title = form.title.data
    feed.url = form.url.data

    # 一覧画面へリダイレクト
    # TODO 自分の一覧にリダイレクト
    redirect("../")



@post('/<feed_id:int>/delete')
def destroy(db, feed_id):
    # Feedの検索
    feed = models.get_feed(db, feed_id)

    # Feedが存在しない(404を表示）
    if not feed:
        return HTTPError(404, 'Feed is not found.')

    # feedを削除
    db.delete(feed)

    # 一覧画面へリダイレクト
    redirect("../")


if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True, reloader=True)
