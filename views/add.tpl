% rebase('base.tpl', feeds=feeds)

<div class="col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main">
    <h1 class="page-header">RSS登録</h1>

    <div class="col-md-5">

        <form action="./add" method="post">

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

            <input type="submit" class="btn btn-default" value="登録する"/>

        </form>
    </div>
</div>
