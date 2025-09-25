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
            # First, check if there are any null values
            cursor.execute("SELECT COUNT(*) FROM job_job WHERE city_id IS NULL")
            null_count = cursor.fetchone()[0]
            
            if null_count > 0:
                print(f"Found {null_count} jobs with null city_id, fixing...")
                
                # Create default city using raw SQL to avoid Django model issues
                cursor.execute("""
                    INSERT INTO address_country (name, code) 
                    VALUES ('United States', 'US') 
                    ON CONFLICT (code) DO NOTHING
                """)
                
                cursor.execute("""
                    INSERT INTO address_state (name, country_id) 
                    SELECT 'Unknown State', id FROM address_country WHERE code = 'US'
                    ON CONFLICT DO NOTHING
                """)
                
                cursor.execute("""
                    INSERT INTO address_city (name, state_id) 
                    SELECT 'Unknown City', id FROM address_state WHERE name = 'Unknown State'
                    ON CONFLICT DO NOTHING
                """)
                
                # Make the column nullable temporarily
                cursor.execute("""
                    ALTER TABLE job_job 
                    ALTER COLUMN city_id DROP NOT NULL
                """)
                
                # Update null values using raw SQL
                cursor.execute("""
                    UPDATE job_job 
                    SET city_id = (
                        SELECT id FROM address_city 
                        WHERE name = 'Unknown City' 
                        LIMIT 1
                    )
                    WHERE city_id IS NULL
                """)
                
                # Verify no null values remain
                cursor.execute("SELECT COUNT(*) FROM job_job WHERE city_id IS NULL")
                remaining_nulls = cursor.fetchone()[0]
                
                if remaining_nulls > 0:
                    print(f"Warning: {remaining_nulls} null values still exist after population")
                else:
                    print("All null values have been populated")
                
                # Make the column NOT NULL again
                cursor.execute("""
                    ALTER TABLE job_job 
                    ALTER COLUMN city_id SET NOT NULL
                """)
            else:
                print("No null city_id values found, skipping population")


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
