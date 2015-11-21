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
            <a class="navbar-brand" href="./">おうぎリーダー(てすと)</a>
        </div>
    </div>
</nav>

<div class="container-fluid">
    <div class="row">
        <div class="col-sm-3 col-md-2 sidebar">
                <!-- <li class="btn"> -->
                    % if request.path == "/add":
                        % add_status = "active"
                    % else:
                        % add_status = ""
                    % end
                    <a href="./add" type="button" class="btn btn-primary navbar-btn btn-block {{add_status}}" role="button">
                        <span class="glyphicon glyphicon-plus"></span> フィード登録
                    </a>
                <!-- </li> -->
            <ul class="nav nav-sidebar">
                <!-- not yet impl favorite -->
                <li class="disabled">
                    % if request.path == "/fav" and request is not None:
                        % fav_status = "active bold"
                    % elif request is not None:
                        % fav_status = "bold"
                    % else:
                        % fav_status = ""
                    % end
                    <li class="{{fav_status}}">
                        <a href="./fav"><span class="glyphicon glyphicon-bookmark"></span> Favorite 10</a>
                    </li>
                </li>

            % if request.path == "/" and request is not None:
                % all_status = "active bold"
            % elif request is not None:
                % all_status = "bold"
            % else:
                % all_status = ""
            % end
            <li class="{{all_status}}">
                <a href="./"><span class="glyphicon glyphicon-list-alt"></span> All 10</a>
            </li>


            % if feeds:
                <li class="nav-divider"></li>
                % for feed in feeds:
                    % if request.path == "/" + str(feed.id) and feed is not None:
                        % feed_status = "active bold"
                    % elif feed is not None:
                        % feed_status = "bold"
                    % else:
                        % feed_status = ""
                    % end
                    <li class="{{feed_status}}">
                        <a href="./{{feed.id}}">{{feed.title}} 10</a>
                    </li>
                % end
            % end
            </ul>
        </div>

        {{!base}}

    </div>
</div>

% include('footer.tpl')
