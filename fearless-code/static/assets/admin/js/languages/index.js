$(document).ready(function () {

    let languages_list_table = $(document).find('#admin-languages-list-view').dataTable({
        serverSide: true,
        sAjaxSource: ADMIN_LANGUAGES_LIST,

        columns: [
            { name: "uuid", data: 0, visible: false },
            { name: "code", data: 1},  
            { name: "name", data: 2},  
            {
                name: "action",
                data: null,
                render: function (data, type, row) {
                    return `<a href="languages/edit/${row[0]}" class="action-icon editBtn">
                                <i class="mdi mdi-square-edit-outline"></i></a>
                            <a href="javascript:void(0);" class="action-icon confirmDeletion" data-uuid="${row[0]}">
                                <i class="mdi mdi-delete" data-bs-toggle="modal"></i></a>`;
                }
            }
        ],
        order: [[2, 'asc']],
    });
    
    

    // Open Confirm Delete Modal
    $(document).on("click",".confirmDeletion",function(){
        let uuid = $(this).attr("data-uuid");
        if(uuid){
            $(".deleteBtn").attr("data-uuid",uuid);
            $("#delete-alert-modal").modal('toggle');
        }
    });

    // Delete Type After Confirmation
    $(document).on("click",".deleteBtn",function(){
        let uuid = $(this).attr("data-uuid");
        $.ajax({
            url: `/admin/languages/delete/${uuid}`,  
            type: 'POST',
            data:{"csrfmiddlewaretoken":$('input[name="csrfmiddlewaretoken"]').val()},
            success: function(data) {
                if(data.success){
                    languages_list_table.api().ajax.reload();
                    toastr.success(data.message);
                }else{
                    toastr.error(data.error);
                }
            }  
        });
    });

});