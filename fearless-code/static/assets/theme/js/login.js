$(document).ready(function(){

    // Admin Login
    $(document).on('click','#sign_in_button',function(){
        
        $("#admin_signin_form").validate({
            rules: {
                email: {required: true,email:true},
                password: {required: true}
            },
            submitHandler: function (form) {
                login_admin();
            }
        });

        // Admin login functionality
        function login_admin(){
            let email = $("input[name='email']").val();
            let password = $("input[name='password']").val();
            $("#signInBtn").text('Loading...');
            $.ajax({
                url: admin_login,  
                type: 'POST',
                data:{"csrfmiddlewaretoken":$('input[name="csrfmiddlewaretoken"]').val(),email,password},
                success: function(data) {
                    $("#sign_in_button").text('Log In');
                    if(data.success){
                        toastr.success(data.message);
                        window.location.href = admin_dashboard;
                    }else{
                        toastr.error(data.error);
                    }
                }  
            });
        }
    });
});