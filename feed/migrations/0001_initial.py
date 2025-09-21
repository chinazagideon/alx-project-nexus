from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[('job_posted', 'Job Posted'), ('company_joined', 'Company Joined'), ('promotion_active', 'Promotion Active')], max_length=50)),
                ('object_id', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('score', models.DecimalField(decimal_places=6, max_digits=20)),
                ('is_active', models.BooleanField(default=True)),
                ('meta', models.JSONField(blank=True, default=dict)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'ordering': ['-score', '-id'],
            },
        ),
        migrations.AddIndex(
            model_name='feeditem',
            index=models.Index(fields=['-score', 'id'], name='feeditem_score_id_idx'),
        ),
        migrations.AddIndex(
            model_name='feeditem',
            index=models.Index(fields=['content_type', 'object_id'], name='feeditem_ct_oid_idx'),
        ),
        migrations.AddIndex(
            model_name='feeditem',
            index=models.Index(fields=['event_type', 'is_active'], name='feeditem_event_active_idx'),
        ),
        migrations.AddConstraint(
            model_name='feeditem',
            constraint=models.UniqueConstraint(condition=models.Q(('is_active', True)), fields=('event_type', 'content_type', 'object_id'), name='unique_active_feed_item_per_object'),
        ),
    ]


