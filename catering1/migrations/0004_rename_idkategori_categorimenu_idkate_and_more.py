# Generated by Django 5.1.1 on 2024-10-29 14:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catering1', '0003_categorimenu_alter_cateringmenu_idkategori'),
    ]

    operations = [
        migrations.RenameField(
            model_name='categorimenu',
            old_name='idKategori',
            new_name='idKate',
        ),
        migrations.RenameField(
            model_name='cateringmenu',
            old_name='idKategori',
            new_name='idKate',
        ),
    ]
