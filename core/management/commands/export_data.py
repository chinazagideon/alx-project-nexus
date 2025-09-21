"""
Management command to export data to JSON files for backup/restore.
Usage: python manage.py export_data [--output-dir=./data_exports]
"""
import json
import os
from django.core.management.base import BaseCommand
from django.core.serializers import serialize
from django.apps import apps


class Command(BaseCommand):
    help = 'Export application data to JSON files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='./data_exports',
            help='Directory to save exported data (default: ./data_exports)',
        )
        parser.add_argument(
            '--models',
            nargs='+',
            help='Specific models to export (e.g., user.User company.Company)',
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        os.makedirs(output_dir, exist_ok=True)
        
        # Define models to export (in dependency order)
        models_to_export = [
            'skill.Skill',
            'address.Address', 
            'company.Company',
            'user.User',
            'job.Job',
            'promotion.Promotion',
            'skill.JobSkill',
            'skill.UserSkill',
        ]
        
        if options['models']:
            models_to_export = options['models']
        
        self.stdout.write(f'Exporting data to {output_dir}...')
        
        for model_path in models_to_export:
            try:
                app_label, model_name = model_path.split('.')
                model = apps.get_model(app_label, model_name)
                
                # Export data
                data = serialize('json', model.objects.all())
                
                # Save to file
                filename = f'{app_label}_{model_name}.json'
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'w') as f:
                    f.write(data)
                
                count = model.objects.count()
                self.stdout.write(f'Exported {count} {model_path} records to {filename}')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error exporting {model_path}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Data export completed! Files saved to {output_dir}')
        )
