% rebase('base.tpl', app_root=app_root, feeds=feeds)

<div class="col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main">
    % if feed is None:
        <h1 class="page-header">全フィードの記事一覧</h1>
    % else:
        <h1 class="page-header">{{feed.title}}の記事一覧</h1>

        <div class="row">
            <div class="pull-right btn-list">
                <ul class="list-inline">
                    <li class="btn-edit"><a href="./{{feed.id}}/edit" type="button" class="btn btn-sm btn-default" role="button">フィード編集</a></li>
                    <li class="btn-edit">
                        <form action="./{{feed.id}}/delete" method="post">
                            <input type="submit" class="btn btn-sm btn-default" value="フィード削除"/>
                        </form>
                    </li>
                </ul>
            </div>
       </div>
    % end


    % if errors:
         <div class="errors">
         % for error in errors:
             <p class="text-danger">{{ error }}</p>
         % end
         </div>
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
            % if entries:
                % for entry in entries:
                    % if entry.read:
                    <tr class="clickable" data-toggle="collapse" data-target="#{{entry.id}}">
                    % else:
                    <tr class="clickable active" data-toggle="collapse" data-target="#{{entry.id}}">
                    % end

                    <td>{{entry.feed.title}}</td>
                    % if entry.read:
                    <td><a href="{{entry.url}}" target="_blank">{{entry.title}}</a></td>
                    % else:
                    <td class="bold"><a href="{{entry.url}}" target="_blank">{{entry.title}}</a></td>
                    % end
                    <td>{{entry.published_at}}</td>
                </tr>
                <tr>
                    <td colspan="3" class="hidden-row">
                        <div id="{{entry.id}}" class="collapse">
                            <p class="description">{{entry.description}}</p>
                        </div>
                    </td>
                </tr>
                % end
            % end
            </tbody>
        </table>
    </div>

    % if feed is None:
        % include('pagination.tpl', pagination=pagination, feed_id="")
    % else:
        % include('pagination.tpl', pagination=pagination, feed_id=feed.id)


</div>
