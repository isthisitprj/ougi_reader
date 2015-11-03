% rebase('base.tpl')

<div class="col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main">
    <h1 class="page-header">RSS登録</h1>

    <div class="col-md-5">

        <form action="/feeds/add" method="post">

            <div class="form-group">
                <label for="title">タイトル</label>
                <input id="title" name="title" type="text" class="form-control" maxlength="100" placeholder="タイトルを入力">
            </div>

            <div class="form-group">
                <label for="url">URL</label>
                <input id="url" name="url" type="text" class="form-control" maxlength="10" placeholder="URLを入力">
            </div>


            <input type="submit" class="btn btn-default" value="登録する"/>

        </form>
    </div>
</div>
