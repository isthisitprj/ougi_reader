% include('header.tpl')

<body>

<nav class="navbar navbar-inverse navbar-fixed-top">
    <div class="container-fluid">
        <div class="navbar-header">
            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                <span class="sr-only">Toggle navigation</span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
            </button>
            <a class="navbar-brand" href="#">おうぎリーダー(てすと)</a>
        </div>
    </div>
</nav>

<div class="container-fluid">
    <div class="row">
        <div class="col-sm-3 col-md-2 sidebar">

            <ul class="nav nav-sidebar">
            % if request.path == "/":
                <li class="active"><a href="./">一覧</a></li>
            % else:
                <li ><a href="./">一覧</a></li>
            % end

            % if feeds:
                <li class="nav-divider"></li>
                % for feed in feeds:
                    % if request.path == "/" + str(feed.id):
                        <li class="active"><a href="./{{feed.id}}">{{feed.title}}</a></li>
                    % else:
                        <li ><a href="./{{feed.id}}">{{feed.title}}</a></li>
                    % end
                % end
                <li class="nav-divider"></li>
            % end

            % if request.path == "/add":
                <li class="active"><a href="./add">RSS登録</a></li>
            % else:
                <li ><a href="./add">RSS登録</a></li>
            % end

                <li class="nav-divider"></li>
            </ul>
        </div>

        {{!base}}

    </div>
</div>

% include('footer.tpl')
