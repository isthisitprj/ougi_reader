% rebase('base.tpl')

<div class="col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main">
    % if title is None:
        <h1 class="page-header">全フィードの記事一覧</h1>
    % else:
        <h1 class="page-header">{{title}}の記事一覧</h1>
    % end

    <div class="table-responsive">
        <table class="table table-striped">
            <thead>
            <tr>
                <th>フィード</th>
                <th>タイトル</th>
                <th>更新日</th>
            </tr>
            </thead>
            <tbody>

            % for entry in entries:
            <tr>
                <td>{{entry.feed.title}}</td>
                <td><a href="{{entry.url}}" target="_blank">{{entry.title}}</a></td>
                <td>{{entry.published_at}}</td>
            </tr>
            % end
            </tbody>
        </table>
    </div>
</div>
