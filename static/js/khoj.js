// USE of this JS File is to enhance user experience by adding interactivity and dynamic behavior to the web application
// This includes features like auto-dismissable alerts, image previews, and confirmation prompts.

document.addEventListener('DOMContentLoaded', function () {
// waits until the full HTML page is completely loaded
// necessary because JavaScript should run only after all elements exist in DOM

    // Auto-dismiss alert messages after 5 seconds
    // improves UX by automatically removing temporary notifications

    const alerts = document.querySelectorAll('.alert.alert-dismissible');
    // selects all Bootstrap alert boxes that can be dismissed/closed
    // querySelectorAll returns all matching elements as a NodeList

    alerts.forEach(function (alert) {
    // loop through every alert message one by one

        setTimeout(function () {
        // runs code after a delay
        // here delay = 5000ms = 5 seconds

            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            // gets existing Bootstrap alert instance
            // or creates one if it doesn't already exist
            // needed because Bootstrap controls alert behavior internally

            if (bsAlert) bsAlert.close();
            // if alert instance exists,
            // automatically close/remove the alert box
        }, 5000);
        // 5000 milliseconds = 5 seconds delay
    });


    // Preview uploaded image before form submission
    // helps user see selected image instantly before uploading

    // Attach to all file inputs that have a sibling .img-preview element

    const fileInputs = document.querySelectorAll('input[type="file"]');
    // selects all file upload input fields from page

    fileInputs.forEach(function (input) {
    // loop through every file input field

        input.addEventListener('change', function () {
        // runs whenever user selects a new file

            const preview = input.parentElement.querySelector('.img-preview');
            // searches inside parent container for image preview element
            // usually an <img> tag used to display selected image

            if (!preview) return;
            // if preview element does not exist,
            // stop execution to avoid errors

            const file = input.files[0];
            // gets the first uploaded file from input field

            if (file && file.type.startsWith('image/')) {
            // checks:
            // 1. file actually exists
            // 2. uploaded file is an image type

                const reader = new FileReader();
                // FileReader allows JavaScript to read uploaded file content
                // needed for showing image preview without uploading to server

                reader.onload = function (e) {
                // runs after file is successfully read

                    preview.src = e.target.result;
                    // sets preview image source to uploaded image data

                    preview.style.display = 'block';
                    // makes preview image visible on page
                };

                reader.readAsDataURL(file);
                // converts image file into Base64 URL format
                // browser can directly display this as image preview
            }
        });
    });


    // Confirm before any form with data-confirm attribute submits
    // prevents accidental delete/update actions

    document.querySelectorAll('[data-confirm]').forEach(function (el) {
    // selects all elements having data-confirm attribute
    // usually buttons like delete/verify/reject

        el.addEventListener('click', function (e) {
        // runs when user clicks that element

            if (!confirm(el.dataset.confirm)) {
            // opens browser confirmation popup
            // message comes from data-confirm attribute value
            // confirm() returns true for OK and false for Cancel

                e.preventDefault();
                // stops default action if user clicks Cancel
                // prevents form submission or dangerous action like deleting a record or updating user information i.e. changing user roles
            }
        });
    });

});
// closes DOMContentLoaded event listener