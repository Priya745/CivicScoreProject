import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'civicscore.settings')
django.setup()
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()

try:
    user = User.objects.get(username='pk')
    print(f'Username : {user.username}')
    print(f'Email    : "{user.email}"')
    print(f'Email empty: {not bool(user.email)}')

    if not user.email:
        print('\nPROBLEM: User pk has NO email saved in the database.')
        print('That is why no email is being sent.')
    else:
        print(f'\nSending test email to {user.email} ...')
        try:
            send_mail(
                subject='CivicScore - Activity Approved (Test)',
                message=f'Hi {user.username},\n\nYour activity has been APPROVED!\n\n- The CivicScore Team',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            print('SUCCESS: Email sent to user pk!')
        except Exception as e:
            print(f'SMTP ERROR: {type(e).__name__}: {e}')

except User.DoesNotExist:
    print('User "pk" not found. All users in the database:')
    for u in User.objects.all():
        print(f'  - username="{u.username}" | email="{u.email}"')
