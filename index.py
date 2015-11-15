# -*- coding: utf-8 -*-
"""index - routing for ougi reader."""

from bottle import HTTPError, get, post, redirect, request, run, template

from wtforms import StringField, validators
from wtforms.form import Form

import feedmanager
import models


class FeedForm(Form):

    """Form for add feed page (maybe and edit feedpage)."""

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
    feeds = models.get_all_feeds(db)

    # feedの更新
    errors = feedmanager.update_feeds(feeds)

    # entriesテーブルから全件取得
    entries = models.get_entries(db)

    # index.tplの描画
    return template('index', feeds=feeds, title=None, entries=entries,
                    errors=errors, request=request)


@get('/add')
def new(db):
    feeds = models.get_all_feeds(db)

    form = FeedForm()

    # add.tplの描画
    return template('add', feeds=feeds, form=form, request=request)


@post('/add')
def create(db):
    feeds = models.get_all_feeds(db)
    form = FeedForm(request.forms.decode())

    # フォームのバリデーション
    if not form.validate():
        return template('add', feeds=feeds, form=form, request=request)

    # Feedの生成と格納
    feed = models.add_feed(db,
                           title=form.title.data,
                           url=form.url.data,
                           )

    feed = feedmanager.setup_feed(feed)

    if feed is None:
        form.url.errors.append(u"URLからフィードを取得できませんでした。")
        return template('add', feeds=feeds, form=form, request=request)

    # feedを既存から検索し、重複していればエラー扱い&コミットしない
    same_url_feed = models.get_same_url_feed(db, feed.url)

    if same_url_feed is not None:
        form.url.errors.append(
            u"すでに同じフィードが登録されています。(「%s」)" % feed.title)
        # insertしてしまっているので、元に戻す(1行だけなので、modelsにはとりあえず入れないでおく)
        db.delete(feed)
        return template('add', feeds=feeds, form=form, request=request)

    # 該当フィードの記事の一覧画面へリダイレクト(リダイレクト先で更新処理が行われる)
    redirect("./" + str(feed.id))


@get('/<feed_id:int>')
def show_entry_list(db, feed_id):
    feeds = models.get_all_feeds(db)

    # Feedの検索
    feed = models.get_feed(db, feed_id)
    # Feedが存在しない(404を表示）
    if not feed:
        return HTTPError(404, 'Feed is not found.')

    # feedの更新
    errors = feedmanager.update_feed(feed)
    entries = models.get_entries(db, feed_id)

    # index.tplの描画
    return template('index', feeds=feeds, title=feed.title, entries=entries,
                    errors=errors, request=request)


@get('/<feed_id:int>/edit')
def edit(db, feed_id):
    feeds = models.get_all_feeds(db)

    # Feedの検索
    feed = models.get_feed(db, feed_id)

    # Feedが存在しない(404を表示）
    if not feed:
        return HTTPError(404, 'Feed is not found.')

    # フォームを作成
    form = FeedForm(request.POST, feed)

    # edit.tplを描画
    return template('edit', feeds=feeds, feed=feed, form=form, request=request)


@post('/<feed_id:int>/edit')
def update(db, feed_id):
    feeds = models.get_all_feeds(db)

    # Feedの検索
    feed = models.get_feed(db, feed_id)

    # Feedが存在しない(404を表示）
    if not feed:
        return HTTPError(404, 'Feed is not found.')

    form = FeedForm(request.forms.decode())

    if not form.validate():
        return template('edit', feeds=feeds, form=form, request=request)

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
