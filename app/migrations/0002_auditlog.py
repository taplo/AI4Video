from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(null=True, verbose_name='用户ID')),
                ('username', models.CharField(max_length=150, verbose_name='用户名')),
                ('ip_address', models.GenericIPAddressField(verbose_name='IP地址')),
                ('action', models.CharField(choices=[('login', '登录'), ('logout', '登出'), ('login_failed', '登录失败'), ('create', '创建'), ('update', '更新'), ('delete', '删除')], max_length=20, verbose_name='操作')),
                ('resource', models.CharField(max_length=200, verbose_name='资源')),
                ('details', models.JSONField(default=dict, verbose_name='详情')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='时间戳')),
                ('success', models.BooleanField(default=True, verbose_name='是否成功')),
            ],
            options={
                'verbose_name': '审计日志',
                'verbose_name_plural': '审计日志',
                'db_table': 'av_audit_log',
                'indexes': [models.Index(fields=['-timestamp'], name='audit_ts_idx'), models.Index(fields=['user_id', 'timestamp'], name='audit_user_ts_idx')],
            },
        ),
    ]
