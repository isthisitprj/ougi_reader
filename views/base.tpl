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
            <a class="navbar-brand" href="{{app_root}}">おうぎリーダー(てすと)</a>
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
                    <a href="{{app_root}}add" type="button" class="btn btn-primary navbar-btn btn-block {{add_status}}" role="button">
                        <span class="glyphicon glyphicon-plus"></span> フィード登録
                    </a>
                <!-- </li> -->
            <ul class="nav nav-sidebar">
                <!-- not yet impl favorite -->
                <li class="disabled">
                    % fav_status = ""
                    % if request.path == "/fav":
                        % fav_status += "active "
                    % end
                    % if 0 < fav_unread_num:
                        % fav_status += "bold "
                    % end
                    <li class="{{fav_status}}">
                        <a href="{{app_root}}fav">
                            <span class="glyphicon glyphicon-bookmark"></span> Favorite
                            % if 0 < fav_unread_num:
                                <span class="badge">{{fav_unread_num}}</span>
                            % end
                        </a>
                    </li>
                </li>

            % all_status = ""
            % if request.path == "/":
                % all_status += "active "
            % end
            % if 0 < all_unread_num:
                % all_status += "bold "
            % end
            <li class="{{all_status}}">
                <a href="{{app_root}}">
                    <span class="glyphicon glyphicon-list-alt"></span> All
                    % if 0 < all_unread_num:
                        <span class="badge">{{all_unread_num}}</span>
                    % end
                </a>
            </li>


            % if feeds:
                <li class="nav-divider"></li>
                % for feed in feeds:
                    % unread_num = feed.unread_num
                    % feed_status = ""
                    % if request.path == "/" + str(feed.id):
                        % feed_status += "active "
                    % end
                    % if 0 < unread_num:
                        % feed_status += "bold "
                    % end
                    <li class="{{feed_status}}">
                        <a href="{{app_root}}{{feed.id}}">{{feed.title}}
                            % if 0 < unread_num:
                                <span class="badge">{{unread_num}}</span>
                            % end
                        </a>
                    </li>
                % end
            % end
            </ul>
        </div>

        {{!base}}

    </div>
</div>

% include('footer.tpl')
