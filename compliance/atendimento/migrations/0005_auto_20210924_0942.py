# Generated by Django 3.1.7 on 2021-09-24 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0004_auto_20210922_1628'),
    ]

    operations = [
        migrations.AddField(
            model_name='atendimento',
            name='solicitante',
            field=models.CharField(max_length=100, null=True, verbose_name='Solicitante'),
        ),
        migrations.AlterField(
            model_name='atendimento',
            name='previsao_dt',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Previsão inicio'),
        ),
    ]
