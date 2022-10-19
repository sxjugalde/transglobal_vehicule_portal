# Generated by Django 3.1.1 on 2020-09-03 20:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('parts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseassembly',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchaseassembly_createdby', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='purchaseassembly',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchaseassembly_modifiedby', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='purchaseassembly',
            name='parts',
            field=models.ManyToManyField(through='parts.PurchaseAssemblyPart', to='parts.Part'),
        ),
        migrations.AddField(
            model_name='part',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='part_createdby', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='part',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='part_modifiedby', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='purchaseassemblypart',
            constraint=models.UniqueConstraint(fields=('purchase_assembly', 'part'), name='unique_purchase_assembly_part'),
        ),
        migrations.AddConstraint(
            model_name='part',
            constraint=models.UniqueConstraint(fields=('code', 'suffix', 'revision'), name='unique_part_identification'),
        ),
    ]
