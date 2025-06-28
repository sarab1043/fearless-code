$(document).ready(function () {

    function init() {
        let resource_type = $(document).find("select[name='type']").val();
        show_hide_fields(resource_type);
    }
    init();

      function show_hide_fields(resource_type) {
        if (resource_type === "link") {
            $("label[for='id_link'], input[name='link']").show();
            $("label[for='id_file'], input[name='file']").hide().val("");
            $("label[for='id_thumbnail'], input[name='thumbnail']").show();
        } else {
            $("label[for='id_link'], input[name='link']").hide().val("");
            $("label[for='id_file'], input[name='file']").show();
            $("label[for='id_thumbnail'], input[name='thumbnail']").show();

        }
    }
    

    $("select[name='type']").on("change", function () {
        show_hide_fields($(this).val());
        clearErrors(); 
    });

    function clearErrors() {
        $(".error-message").remove();
    }

    $("#edit-resources").on("submit", function (e) {
        clearErrors();
        let isValid = true;

        let resource_type = $("select[name='type']").val();
        let fileInput = $("input[name='file']")[0];
        if (!resource_type) {
            showError($("select[name='type']"), "Please select a resource type.");
            isValid = false;
        }

        let allowedExtensions = {
            pdf: ["pdf"],
            doc: ["doc", "docx", "xlsx"],
        };

        if (fileInput.files.length > 0) {
            let fileName = fileInput.files[0].name;
            let fileExt = fileName.split(".").pop().toLowerCase();

            if (!allowedExtensions[resource_type].includes(fileExt)) {
                showError($("input[name='file']"), `Invalid file type. Allowed formats: ${allowedExtensions[resource_type].join(", ").toUpperCase()}`);
                isValid = false;
            }
        }

        if (!isValid) {
            e.preventDefault();
        }
    });

    function showError(element, message) {
        let errorSpan = $("<span>").addClass("error-message text-danger").text(message);
        element.after(errorSpan);
    }

    //image preview
    $(document).on('change', '#id_file', function (event) {
        let fileInput = event.target;
        let file = fileInput.files[0];
        if (file) {
            let reader = new FileReader();
            reader.onload = function (e) {
                $('#file-url').attr('href', e.target.result).text(file.name);
            };
            reader.readAsDataURL(file);
        }
    });

});
