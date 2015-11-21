% rebase('base.tpl', app_root=app_root, feeds=feeds,
%          all_unread_num=all_unread_num)

<div class="col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main">
    % if feed_id is None:
        <h1 class="page-header">RSS登録</h1>
    % else:
        <h1 class="page-header">RSS編集</h1>
    % end

    <div class="col-md-5">

        % if feed_id is None:
            <form action="./add" method="post">
        % else:
            <form action="./edit" method="post">
        % end

        <div class="form-group">
            {{ !form.title.label }}
            {{ !form.title(class_="form-control", placeholder=u"タイトルを入力", maxlength="100") }}

           % if form.title.errors:
                <div class="errors">
                % for error in form.title.errors:
                    <p class="text-danger">{{ error }}</p>
                % end
                </div>
            % end
        </div>

        <div class="form-group">
            {{ !form.url.label }}
            {{ !form.url(class_="form-control", placeholder=u"URLを入力", maxlength="2000") }}

           % if form.url.errors:
                <div class="errors">
                % for error in form.url.errors:
                    <p class="text-danger">{{ error }}</p>
                % end
                </div>
            % end
        </div>

        % if feed_id is None:
            <input type="submit" class="btn btn-default" value="作成する"/>
        % else:
            <input type="submit" class="btn btn-default" value="更新する"/>
        % end

        </form>
    </div>
</div>
