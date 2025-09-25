# Generated manually to fix city field null values

from django.db import migrations, models


def populate_city_data(apps, schema_editor):
    """Populate city_id for existing jobs that have null values"""
    Job = apps.get_model('job', 'Job')
    City = apps.get_model('address', 'City')
    State = apps.get_model('address', 'State')
    Country = apps.get_model('address', 'Country')
    
    # Get or create a default city
    default_city = City.objects.first()
    
    if not default_city:
        # Create a default country, state, and city if none exist
        default_country, created = Country.objects.get_or_create(
            name='United States',
            defaults={'code': 'US'}
        )
        
        default_state, created = State.objects.get_or_create(
            name='Unknown State',
            defaults={'country': default_country}
        )
        
        default_city, created = City.objects.get_or_create(
            name='Unknown City',
            defaults={'state': default_state}
        )
    
    # Update all jobs with null city_id
    jobs_with_null_city = Job.objects.filter(city__isnull=True)
    updated_count = jobs_with_null_city.update(city=default_city)
    
    print(f"Updated {updated_count} jobs with city_id")


def fix_postgresql_constraint(apps, schema_editor):
    """Handle PostgreSQL constraint issues using raw SQL"""
    if schema_editor.connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            # First, make the column nullable using raw SQL
            cursor.execute("""
                ALTER TABLE job_job 
                ALTER COLUMN city_id DROP NOT NULL
            """)
            
            # Populate the data
            populate_city_data(apps, schema_editor)
            
            # Make the column NOT NULL again
            cursor.execute("""
                ALTER TABLE job_job 
                ALTER COLUMN city_id SET NOT NULL
            """)


def reverse_populate_city_data(apps, schema_editor):
    """Reverse migration - no-op since we can't reliably identify which jobs were updated"""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('address', '0001_initial'),
        ('job', '0003_alter_job_city'),
    ]

    operations = [
        migrations.RunPython(fix_postgresql_constraint, reverse_populate_city_data),
    ]
