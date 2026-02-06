from django.db import migrations, models
import django.utils.timezone
import ckeditor.fields

class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250)),
                ('status', models.CharField(choices=[('Draft', 'Draft'), ('Published', 'Published')], default='Draft', max_length=20)),
                ('category', models.CharField(blank=True, max_length=100, null=True)),
                ('url_city', models.CharField(blank=True, max_length=100, null=True)),
                ('district', models.CharField(blank=True, max_length=100, null=True)),
                ('content', ckeditor.fields.RichTextField(blank=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='news_pics/')),
                ('image_url', models.URLField(blank=True, max_length=500, null=True)),
                ('youtube_url', models.URLField(blank=True, null=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('slug', models.SlugField(blank=True, max_length=500, unique=True)),
                ('share_now_to_fb', models.BooleanField(default=False, verbose_name='Facebook post?')),
                ('is_fb_posted', models.BooleanField(default=False)),
                ('is_important', models.BooleanField(default=False, verbose_name='Breaking News?')),
                ('meta_keywords', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'mynews_news_v5',  # Nayi table v5
            },
        ),
    ]
