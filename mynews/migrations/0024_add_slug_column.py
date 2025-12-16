from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ("mynews", "0021_merge_0018_alter_news_slug_0020_fake_forward_slug_fix"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE mynews_news
            ADD COLUMN IF NOT EXISTS slug VARCHAR(350);
            """,
            reverse_sql="""
            ALTER TABLE mynews_news
            DROP COLUMN IF EXISTS slug;
            """
        ),
    ]