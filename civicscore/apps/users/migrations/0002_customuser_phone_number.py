from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="phone_number",
            field=models.CharField(default="0000000000", max_length=20),
        ),
    ]
