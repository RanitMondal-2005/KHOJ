// Global JS for Khoj - runs on every page via base.html

document.addEventListener('DOMContentLoaded', function () {
    // wait until full HTML is loaded before running anything

    // auto-dismiss Django flash messages after 5 seconds so, user doesn't have to manually close every alert
    const alerts = document.querySelectorAll('.alert.alert-dismissible');

    alerts.forEach(function (alert) {
        setTimeout(function () {
            // Bootstrap's Alert instance controls the close animation
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000); // 5 seconds
    });
});