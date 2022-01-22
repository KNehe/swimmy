# Generated by Django 4.0 on 2022-01-22 14:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customuser', '0001_initial'),
        ('restful', '0006_alter_rating_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='pool',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rating', to='restful.pool'),
        ),
        migrations.CreateModel(
            name='FileUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=50)),
                ('file', models.FileField(upload_to='media/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='customuser.user')),
            ],
        ),
    ]