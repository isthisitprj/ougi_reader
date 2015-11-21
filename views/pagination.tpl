<div class="pagination-layout">
    <ul class="pagination pagination-lg">
    % if pagination.has_prev:
        <li class="prev">
            <a href="./{{feed_id}}?page={{ pagination.page - 1 }}">Prev</a>
        </li>
    % end
    % for page in pagination.iter_pages():
        % if page:
            % if page == pagination.page:
                <li class="active"><a href="./{{feed_id}}?page={{ page }}">{{ page }}</a></li>
            % else:
                <li><a href="./{{feed_id}}?page={{ page }}">{{ page }}</a></li>
            % end
        % else:
              <li class="disabled"><a>...</a></li>
        % end
    % end
    % if pagination.has_next:
        <li class="next">
            <a href="./{{feed_id}}?page={{ pagination.page + 1 }}">Next</a>
        </li>
    % end
    </ul>
</div>
