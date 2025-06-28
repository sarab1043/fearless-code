$(document).ready(function(){

  
    let users_quiz_result_list_view = $(document).find('#admin-users-quiz-result-view').dataTable({
        serverSide: true,
        sAjaxSource: ADMIN_USER_QUIZ_RESULT_LIST,
        columns: [
            {name:"uuid", data:0, visible:false},
            {name: "question__question_text", data: 1},
            {name: "selected_option__text", data: 2},
            {name:"is_correct",data: 3, 
                render: function (data, type, row) {
                    if (type === 'display') {
                        if (data === true || data === 'true') {
                            return '<span class="badge bg-success p-1">Correct</span>';
                        } else if (data === false || data === 'false') {
                            return '<span class="badge bg-danger p-1">Incorrect</span>';
                        } else {
                            return '<span class="badge badge-secondary">-</span>';
                        }
                    }
                    return data;
                }
            },
            {name: "selected_option__points", data: 4},

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
            
        ],
        order: [[5, 'asc']],
    });
})