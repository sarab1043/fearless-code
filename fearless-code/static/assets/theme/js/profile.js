$(document).ready(function(){
    // Validate change password form
    $(document).on('click','#updatePasswordBtn',function(){
        $("#update-password-form").validate({
            rules: {
                password: {required: true,minlength: 6},
                confirm_password: {
                    minlength: 8,
                    required: true,
                    equalTo: "#password"
                }
            },
            messages: {
                confirm_password: "Confirm password must be match with new password.",
            }
        });
    });
});