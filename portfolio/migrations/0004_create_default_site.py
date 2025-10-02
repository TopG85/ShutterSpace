from django.db import migrations


def create_default_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    if not Site.objects.exists():
        Site.objects.create(domain='localhost', name='localhost')


class Migration(migrations.Migration):
    dependencies = [
        ('portfolio', '0003_profile_display_name_profile_instagram_and_more'),
        ('sites', '0002_alter_domain_unique'),
    ]
    operations = [
        migrations.RunPython(create_default_site),
    ]
