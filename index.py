# -*- coding: utf-8 -*-
"""index - routing for ougi reader."""

from bottle import HTTPError, get, post, redirect, request, run, template, url

from wtforms import StringField, validators
from wtforms.form import Form

from models import (add_feed, get_all_feeds, get_entries, get_feed,
                    get_sum_of_unread, rollback)

from utils.feedmanager import setup_feed, update_feed, update_feeds
from utils.pagination import Pagination
from utils.viewutils import ENTRIES_PER_PAGE, get_shwon_entries


class FeedForm(Form):

    """Form for add feed page (maybe and edit feedpage)."""

    title = StringField(u"タイトル", [
        validators.Optional(),
        validators.length(min=1, max=100, message=u"100文字以下で入力してください")
    ])
    url = StringField(u"URL", [
        validators.InputRequired(message=u"入力してください"),
        validators.length(min=1, max=2000, message=u"2000文字以下で入力してください")
    ])


def get_app_root():
    return url("app_root_url")


@get("/", name="app_root_url")
def index(db):
    feeds = get_all_feeds(db)

    # パラメータから表示するページ数を取得
    shown_page = request.params.get(key="page", default=1, type=int)

    # feedの更新
    errors = update_feeds(feeds)

    # entriesテーブルから全件取得
    entries = get_entries(db)

    # 表示するページ分だけ切り取る
    # TODO sql投げる時点で一部だけ取得するようにする
    entries, shown_page, total = get_shwon_entries(entries, shown_page)

    # TODO  paginationにshown_pageじゃなくってpageを直接つっこんでいいかどうか
    # ページネイションを生成
    pagination = Pagination(shown_page, ENTRIES_PER_PAGE, total)

    # index.tplの描画
    return template("index", app_root=get_app_root(), feeds=feeds, feed=None,
                    entries=entries, pagination=pagination,
                    errors=errors, request=request,
                    all_unread_num=get_sum_of_unread(db),
                    fav_unread_num=0)


@get("/<feed_id:int>")
def show_entry_list(db, feed_id):
    # Feedの検索
    feed = get_feed(db, feed_id)
    # Feedが存在しない(404を表示）
    if not feed:
        return HTTPError(404, "Feed is not found.")

    # パラメータから表示するページ数を取得
    shown_page = request.params.get(key="page", default=1, type=int)

    # feedの更新
    errors = update_feed(feed)
    entries = get_entries(db, feed_id)

    # 表示するページ分だけ切り取る
    # TODO sql投げる時点で一部だけ取得するようにする
    entries, shown_page, total = get_shwon_entries(entries, shown_page)

    # TODO  paginationにshown_pageじゃなくってpageを直接つっこんでいいかどうか
    # ページネイションを生成
    pagination = Pagination(shown_page, ENTRIES_PER_PAGE, total)

    # index.tplの描画
    return template("index", feeds=get_all_feeds(db),
                    app_root=get_app_root(),  feed=feed,
                    entries=entries, pagination=pagination,
                    errors=errors, request=request,
                    all_unread_num=get_sum_of_unread(db),
                    fav_unread_num=0)


@get("/add")
def new(db):
    form = FeedForm()

    # add.tplの描画
    return template("edit", feeds=get_all_feeds(db),
                    app_root=get_app_root(),
                    feed_id=None, form=form, request=request,
                    all_unread_num=get_sum_of_unread(db),
                    fav_unread_num=0)


@post("/add")
def create(db):
    form = FeedForm(request.forms.decode())

    # フォームのバリデーション
    if not form.validate():
        return template("edit", feeds=get_all_feeds(db),
                        app_root=get_app_root(),
                        feed_id=None, form=form, request=request,
                        all_unread_num=get_sum_of_unread(db),
                        fav_unread_num=0)

    # Feedの生成と格納(コミットも)
    feed = add_feed(db, title=form.title.data, url=form.url.data,)

    feed = setup_feed(feed)

    if feed is None:
        form.url.errors.append(u"URLからフィードを取得できませんでした。")
        return template("edit", feeds=get_all_feeds(db),
                        app_root=get_app_root(),
                        feed_id=None, form=form, request=request,
                        all_unread_num=get_sum_of_unread(db),
                        fav_unread_num=0)

    # feedを既存から検索し、重複していればエラー扱い&コミットしない
    same_url_feed = feed.get_another_feed_with_same_url(db)

    if same_url_feed:
        form.url.errors.append(
            u"すでに同じフィードが登録されています。(「%s」)" % same_url_feed.title)
        # insertしてしまっているので、元に戻す為には削除する
        feed.delete(db)
        return template("edit", feeds=get_all_feeds(db),
                        app_root=get_app_root(),
                        feed_id=None, form=form, request=request,
                        all_unread_num=get_sum_of_unread(db),
                        fav_unread_num=0)

    # 該当フィードの記事の一覧画面へリダイレクト(リダイレクト先で更新処理が行われる)
    redirect(get_app_root() + str(feed.id))


@get("/<feed_id:int>/edit")
def edit(db, feed_id):
    # Feedの検索
    feed = get_feed(db, feed_id)

    # Feedが存在しない(404を表示）
    if not feed:
        return HTTPError(404, "Feed is not found.")

    # フォームを作成
    form = FeedForm(request.POST, feed)

    # edit.tplを描画
    return template("edit", feeds=get_all_feeds(db),
                    app_root=get_app_root(),
                    feed_id=feed_id, form=form, request=request,
                    all_unread_num=get_sum_of_unread(db),
                    fav_unread_num=0)


@post("/<feed_id:int>/edit")
def update(db, feed_id):
    # Feedの検索
    feed = get_feed(db, feed_id)

    # Feedが存在しない(404を表示）
    if not feed:
        return HTTPError(404, "Feed is not found.")

    form = FeedForm(request.forms.decode())

    # フォームのバリデーション
    if not form.validate():
        return template("edit", feeds=get_all_feeds(db),
                        app_root=get_app_root(),
                        feed_id=feed_id, form=form, request=request,
                        all_unread_num=get_sum_of_unread(db),
                        fav_unread_num=0)

    # feed情報を更新
    feed.title = form.title.data
    feed.url = form.url.data

    feed = setup_feed(feed)

    if feed is None:
        form.url.errors.append(u"URLからフィードを取得できませんでした。")
        return template("edit", feeds=get_all_feeds(db),
                        app_root=get_app_root(),
                        feed_id=feed_id, form=form, request=request,
                        all_unread_num=get_sum_of_unread(db),
                        fav_unread_num=0)

    # feedを既存から検索し、重複していればエラー扱い&コミットしない
    same_url_feed = feed.get_another_feed_with_same_url(db)

    if same_url_feed:
        form.url.errors.append(
            u"すでに同じフィードが登録されています。(「%s」)" % same_url_feed.title)
        # addのときと違い、コミットまでははしていない
        rollback(db)
        return template("edit", feeds=get_all_feeds(db),
                        app_root=get_app_root(),
                        feed_id=feed_id, form=form, request=request,
                        all_unread_num=get_sum_of_unread(db),
                        fav_unread_num=0)

    # 該当フィードの記事の一覧画面へリダイレクト(リダイレクト先で更新処理が行われる)
    redirect(get_app_root() + str(feed.id))


@post("/<feed_id:int>/delete")
def destroy(db, feed_id):

    # Feedの検索
    feed = get_feed(db, feed_id)

    # Feedが存在しない(404を表示）
    if not feed:
        return HTTPError(404, "Feed is not found.")

    # feedを削除
    feed.delete(db)

    # 一覧画面へリダイレクト
    redirect(get_app_root())


if __name__ == "__main__":
    run(host="localhost", port=8080, debug=True, reloader=True)
