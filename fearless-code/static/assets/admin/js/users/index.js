$(document).ready(function () {
    let check_status = $('.user-status-filter').val();
    $('.user-status-filter').on('change', function() {
        check_status = $(this).val();
        users_list_table.api().ajax.reload();
    });
    
    let users_list_table = $(document).find('#admin-users-list-view').dataTable({
        serverSide: true,
        sAjaxSource: ADMIN_USERS_LIST,
        fnServerParams: function (aoData) {
            aoData.push({ "name": "check_status", "value": check_status });
        },
        columns: [
            {name:"uuid", data:0, visible:false},
            {name: "name", data: 1},
            {name: "email", data: 2},
            {
                name:"is_active",
                data: 3,
                render: function (data, type, row) {
                    if (type === 'display') {
                        let checked;
                        if(row[3] === true){
                            checked = "checked";
                        }
                        return `<input type="checkbox" id="status_${row[0]}"  ${checked}  data-switch="bool" class="user_status" data-user_uuid="${row[0]}">
                        <label for="status_${row[0]}" data-on-label="Active" data-off-label="InActive"></label>`;
                    }
                    return data;
                }
            },
            {
                name: "created_at",
                data: 4,
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
                        return `
                        <a href="javascript:void(0);" class="action-icon confirmDeletion" data-uuid="${row[0]}"> <i class="mdi mdi-delete" data-bs-toggle="modal"></i></a>`;
                    }
                    return data;
                }
            }
        ],
        order: [[4, 'asc']],
    });
    

    // Change User Status
    $(document).on("change",".user_status",function(){
        let status = false;
        if($(this).is(':checked')){status = true;}
        let user_uuid = $(this).data("user_uuid");
        $.ajax({
            url: `/admin/users/status/${user_uuid}`,  
            type: 'POST',
            data:{"csrfmiddlewaretoken":$('input[name="csrfmiddlewaretoken"]').val(),status,user_uuid},
            success: function(data) {
                if(data.success){
                    toastr.success(data.message); 
                }else{
                    toastr.error(data.error);
                }
            }  
        });
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
            url: `/admin/users/delete/${uuid}`,  
            type: 'POST',
            data:{"csrfmiddlewaretoken":$('input[name="csrfmiddlewaretoken"]').val()},
            success: function(data) {
                if(data.success){
                    users_list_table.api().ajax.reload();
                    toastr.success(data.message);
                }else{
                    toastr.error(data.error);
                }
            }  
        });
    });

});