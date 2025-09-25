"""
Simple command to prepare database before migrations
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Prepare database before migrations'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            try:
                # Check for null values (this will work if table exists)
                cursor.execute("SELECT COUNT(*) FROM job_job WHERE city_id IS NULL")
                null_count = cursor.fetchone()[0]
                
                if null_count > 0:
                    self.stdout.write(f'Found {null_count} null city_id values, fixing...')
                    
                    # Create default city
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
                    
                    # Fix null values
                    cursor.execute("""
                        UPDATE job_job 
                        SET city_id = (
                            SELECT id FROM address_city 
                            WHERE name = 'Unknown City' 
                            LIMIT 1
                        )
                        WHERE city_id IS NULL
                    """)
                    
                    self.stdout.write(self.style.SUCCESS(f'Fixed {null_count} null values'))
                else:
                    self.stdout.write('No null city_id values found')
            except Exception as e:
                self.stdout.write(f'Table not ready yet: {e}')
