import app.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auditlog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='algorithmmodel',
            name='last_update_time',
            field=models.DateTimeField(auto_now=True, verbose_name='更新时间'),
        ),
        migrations.AlterField(
            model_name='bizalgorithmmodel',
            name='last_update_time',
            field=models.DateTimeField(auto_now=True, verbose_name='更新时间'),
        ),
        migrations.AlterField(
            model_name='llmmodel',
            name='api_key',
            field=app.fields.EncryptedCharField(default='', max_length=512, verbose_name='API密钥'),
        ),
        migrations.AlterField(
            model_name='llmmodel',
            name='last_update_time',
            field=models.DateTimeField(auto_now=True, verbose_name='更新时间'),
        ),
        migrations.AlterField(
            model_name='streammodel',
            name='last_update_time',
            field=models.DateTimeField(auto_now=True, verbose_name='更新时间'),
        ),
        migrations.AlterField(
            model_name='streammodel',
            name='pull_stream_password',
            field=app.fields.EncryptedCharField(max_length=255, verbose_name='拉流密码'),
        ),
        migrations.AlterField(
            model_name='zonemodel',
            name='last_update_time',
            field=models.DateTimeField(auto_now=True, verbose_name='更新时间'),
        ),
    ]
