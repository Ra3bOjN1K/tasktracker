function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
});

String.prototype.trimToLength = function(m) {
    return (this.length > m)
        ? jQuery.trim(this).substring(0, m).split(" ").slice(0, -1).join(" ") + "..."
        : this;
};

function buildTaskList(json_tasks) {
    var $data = "";

    $.each(json_tasks, function (idx, $task) {
        $data +=
            '<div class="task_item">' +
                '<div class="task_item__title">' +
                    '<span class="task__name">' + $task.name.trimToLength(40) + '</span>' +
                    '<span class="task__created">' + $.format.date($task.created, "dd-MM-yyyy HH:mm:ss") + '</span>' +
                '</div>' +
                '<span class="task__desc__title">Short description: </span>' +
                '<span class="task__description">' + $task.description.trimToLength(120) + '</span>' +

                '<div class="task_slug_info">' +
                    '<span class="task__executors__title">Executor: </span>' +
                    '<div class="task__executors">' +
                        $task.executors.join(", ") +
                    '</div>' +
                    '<span class="task__creator">' +
                        '<span class="task__creator__title">Author: </span>' + $task.creator +
                    '</span>' +
                    '<span class="task__status">' +
                        '<span class="task__status__title">Status: </span>' + $task.get_verbose_status_val +
                    '</span>' +
                '</div>' +
                '<a class="task_detail" href="/task/' + $task.id + '/details/">Details</a>' +
            '</div>'
    });

    return $data;
}