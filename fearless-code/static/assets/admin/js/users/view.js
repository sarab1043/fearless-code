$(document).ready(function(){

    let quiz_type = $('.all-attempt-quizzes').val();
    $('.all-attempt-quizzes').on('change', function() {
        quiz_type = $(this).val();
        users_attempts_quiz_list_view.api().ajax.reload();
    });
    
    let users_attempts_quiz_list_view = $(document).find('#admin-users-attempts-quiz-view').dataTable({
        serverSide: true,
        sAjaxSource: ADMIN_ATTEMPT_QUIZZESS_LIST,
        fnServerParams: function (aoData) {
            aoData.push({ "name": "quiz_type", "value": quiz_type });
        },
        columns: [
            {name:"uuid", data:0, visible:false},
            {name: "type", data: 1},
            {name:"result",data: 2},
            {name:"result_points",data: 3},
            {name:"status",data: 4,
                render: function (data, type, row) {
                    if (data === "submitted") {
                        return '<span class="badge bg-success p-1">Submitted</span>';
                    } else if (data === "started") {
                        return '<span class="badge bg-primary p-1">Started</span>';
                    } else if (data === "not_participated") {
                        return '<span class="badge bg-secondary p-1">Not Participated</span>';
                    } 
                    return data;
                }
            },
            {
                name: "created_at",
                data: 5,
                render: function (data, type, row) {
                    if (type === 'display') {
                        if (data) {
                            let date = new Date(data);
                            return date.toLocaleString();
                        } else {
                            return "—"; // Or empty string ''
                        }
                    }
                    return data;
                }
            },
            {
                name:"action",
                data: null,
                render: function (data, type, row) {
                    if (type === 'display') {
                        return `<a href="/admin/users/quiz/result/${row[0]}" class="btn btn-sm btn-outline-secondary">View result</a>`;
                    }
                    return data;
                }
            }
        ],
        order: [[5, 'asc']],
    });
})