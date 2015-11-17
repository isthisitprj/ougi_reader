% rebase('base.tpl', feeds=feeds)

<div class="col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main">
    % if title is None:
        <h1 class="page-header">全フィードの記事一覧</h1>
    % else:
        <h1 class="page-header">{{title}}の記事一覧</h1>
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
                <tr class="clickable" data-toggle="collapse" data-target="#{{entry.id}}">
                    <td>{{entry.feed.title}}</td>
                    <td><a href="{{entry.url}}" target="_blank">{{entry.title}}</a></td>
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

    <div class="pagination-layout">
        <ul class="pagination pagination-lg">
            <li class="prev"><a>Prev</a></li>
            <li class="active"><a>1</a></li>
            <li><a>2</a></li>
            <li><a>3</a></li>
            <li><a>...</a></li>
            <li class="next"><a>Next</a></li>
        </ul>
   </div>
</div>
