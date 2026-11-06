from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

app_name = "orders"

urlpatterns = [
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="password_reset/form.html",
            email_template_name="password_reset/email.txt",
            subject_template_name="password_reset/subject.txt",
            success_url=reverse_lazy("orders:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="password_reset/done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="password_reset/confirm.html",
            success_url=reverse_lazy("orders:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="password_reset/complete.html"
        ),
        name="password_reset_complete",
    ),
]
