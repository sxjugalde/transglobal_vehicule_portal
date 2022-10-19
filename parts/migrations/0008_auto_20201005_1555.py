# Generated by Django 3.1.1 on 2020-10-05 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0007_auto_20200923_1200'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseassembly',
            name='full_code',
            field=models.CharField(blank=True, editable=False, max_length=8),
        ),
        migrations.AddField(
            model_name='purchaseassemblypart',
            name='full_code',
            field=models.CharField(blank=True, editable=False, max_length=20),
        ),
        migrations.AddIndex(
            model_name='purchaseassembly',
            index=models.Index(fields=['full_code'], name='parts_purch_full_co_2ef8aa_idx'),
        ),
        migrations.AddIndex(
            model_name='purchaseassemblypart',
            index=models.Index(fields=['full_code'], name='parts_purch_full_co_28aad4_idx'),
        ),
    ]