$(document).ready(function () {

    let resources_list_table = $(document).find('#admin-resources-list-view').dataTable({
        serverSide: true,
        sAjaxSource: ADMIN_RESOURCES_LIST,

        columns: [
            { name: "uuid", data: 0, visible: false },
            { name: "name", data: 1},  
            { name: "type", data: 2},  
            { 
                name: "file", 
                data: 3,
                render: function(data, type, row) {
                    if (!data) return "—";
    
                    let fileName = data.split('/').pop(); 
                    let shortName = fileName.length > 30 ? fileName.substring(0, 30) + "..." : fileName;
                    let fileExt = fileName.split('.').pop().toLowerCase();
                    let icons = {
                        pdf: "📄",
                        doc: "📑",
                        docx: "📑",
                        jpg: "🖼️",
                        jpeg: "🖼️",
                        png: "🖼️",
                        mp4: "🎥",
                        mov: "🎥",
                        avi: "🎥"
                    };
                    let icon = icons[fileExt] || "📁";
                    return `<a href="/media/${data}" target="_blank">${icon} ${shortName}</a>`;
                }
            },
            { name: "link", data: 4, 
                render:function(data, type, row){
                     if (type === 'display') {
                        if (data) {
                            
                            return `<a href="${data}">${data}</a>`
                        } else {
                            return "—"; // Or empty string ''
                        }
                    }
                    return data;
                }
            },
             { name: "thumbnail", data: 5, 
                render:function(data, type, row){
                     if (type === 'display') {
                        if (data) {
                            return `<img src="/media/${data}" width="100px" height="100px" alt="Thumbnail" />`;
                        } else {
                            return "—"; // Or empty string ''
                        }
                    }
                    return data;
                }
            },
            {
                name: "created_at",
                data: 6, 
                render: function (data, row, type) {
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
                name: "action",
                data: null,
                render: function (data, type, row) {
                    return `<a href="resources/edit/${row[0]}" class="action-icon editBtn">
                                <i class="mdi mdi-square-edit-outline"></i></a>
                            <a href="javascript:void(0);" class="action-icon confirmDeletion" data-uuid="${row[0]}">
                                <i class="mdi mdi-delete" data-bs-toggle="modal"></i></a>`;
                }
            }
        ],
        order: [[6, 'desc']],
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
            url: `/admin/resources/delete/${uuid}`,  
            type: 'POST',
            data:{"csrfmiddlewaretoken":$('input[name="csrfmiddlewaretoken"]').val()},
            success: function(data) {
                if(data.success){
                    resources_list_table.api().ajax.reload();
                    toastr.success(data.message);
                }else{
                    toastr.error(data.error);
                }
            }  
        });
    });

});