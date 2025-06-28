$(document).ready(function () {

    function clearErrors() {
        $(".error-message").remove(); // Remove previous error messages
    }

    function showError(element, message) {
        let errorSpan = $("<span>").addClass("error-message text-danger").text(message);
        element.after(errorSpan);
    }

    $("#add-languages").on("submit", function (e) {
        clearErrors();
        let isValid = true;

        let codeInput = $("#id_code");
        let nameInput = $("#id_name");

        if (!codeInput.val().trim()) {
            showError(codeInput, "Language code is required.");
            isValid = false;
        }

        if (!nameInput.val().trim()) {
            showError(nameInput, "Language name is required.");
            isValid = false;
        }

        if (!isValid) {
            e.preventDefault(); // Prevent form submission
        }
    });
});
