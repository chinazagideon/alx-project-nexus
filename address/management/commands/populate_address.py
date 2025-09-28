"""
Management command to manually populate address app with custom data.
Usage: python manage.py populate_address [--country=COUNTRY] [--state=STATE] [--city=CITY] [--location=LOCATION] [--zip-code=ZIP] [--interactive]
"""

import json

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from address.models import Address, City, Country, State
from address.services import AddressService


class Command(BaseCommand):
    help = "Manually populate address app with custom address, city, state, and country data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--country",
            type=str,
            help='Country name (e.g., "United States")',
        )
        parser.add_argument(
            "--country-code",
            type=str,
            help='Country code (e.g., "US")',
        )
        parser.add_argument(
            "--state",
            type=str,
            help='State/Province name (e.g., "California")',
        )
        parser.add_argument(
            "--city",
            type=str,
            help='City name (e.g., "San Francisco")',
        )
        parser.add_argument(
            "--location",
            type=str,
            help='Street address (e.g., "123 Main St")',
        )
        parser.add_argument(
            "--zip-code",
            type=str,
            help='ZIP/Postal code (e.g., "94102")',
        )
        parser.add_argument(
            "--interactive",
            action="store_true",
            help="Run in interactive mode to input data step by step",
        )
        parser.add_argument(
            "--json-file",
            type=str,
            help="Path to JSON file containing address data",
        )
        parser.add_argument(
            "--content-type",
            type=str,
            help='Content type for the address (e.g., "user", "company")',
        )
        parser.add_argument(
            "--object-id",
            type=int,
            help="Object ID for the address relationship",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created without actually creating it",
        )

    def handle(self, *args, **options):
        self.address_service = AddressService()

        if options["interactive"]:
            self.run_interactive_mode()
        elif options["json_file"]:
            self.run_json_file_mode(options["json_file"])
        else:
            self.run_command_line_mode(options)

    def run_interactive_mode(self):
        """Run in interactive mode to collect data step by step"""
        self.stdout.write(self.style.SUCCESS("Running in interactive mode..."))

        # Collect country data
        country_name = self.get_input("Enter country name: ", required=True)
        country_code = self.get_input("Enter country code (e.g., US): ", required=True)

        # Collect state data
        state_name = self.get_input("Enter state/province name: ", required=True)

        # Collect city data
        city_name = self.get_input("Enter city name: ", required=True)

        # Collect address data
        location = self.get_input("Enter street address: ", required=True)
        zip_code = self.get_input("Enter ZIP/postal code: ", required=True)

        # Collect relationship data
        content_type = self.get_input("Enter content type (optional): ", required=False)
        object_id = self.get_input("Enter object ID (optional): ", required=False, input_type=int)

        # Create the address
        address_data = {
            "country_name": country_name,
            "country_code": country_code,
            "state_name": state_name,
            "city_name": city_name,
            "location": location,
            "zip_code": zip_code,
            "content_type": content_type,
            "object_id": object_id,
        }

        self.create_address_from_data(address_data)

    def run_json_file_mode(self, json_file_path):
        """Run with data from JSON file"""
        try:
            with open(json_file_path, "r") as f:
                data = json.load(f)

            if isinstance(data, list):
                for address_data in data:
                    self.create_address_from_data(address_data)
            else:
                self.create_address_from_data(data)

        except FileNotFoundError:
            raise CommandError(f"JSON file not found: {json_file_path}")
        except json.JSONDecodeError as e:
            raise CommandError(f"Invalid JSON file: {e}")

    def run_command_line_mode(self, options):
        """Run with command line arguments"""
        # Validate required fields
        required_fields = ["country", "state", "city", "location", "zip_code"]
        missing_fields = [field for field in required_fields if not options.get(field.replace("-", "_"))]

        if missing_fields:
            raise CommandError(f'Missing required fields: {", ".join(missing_fields)}')

        address_data = {
            "country_name": options["country"],
            "country_code": options.get("country_code", ""),
            "state_name": options["state"],
            "city_name": options["city"],
            "location": options["location"],
            "zip_code": options["zip_code"],
            "content_type": options.get("content_type"),
            "object_id": options.get("object_id"),
        }

        if options["dry_run"]:
            self.show_dry_run(address_data)
        else:
            self.create_address_from_data(address_data)

    def get_input(self, prompt, required=True, input_type=str):
        """Get user input with validation"""
        while True:
            value = input(prompt).strip()

            if not value and required:
                self.stdout.write(self.style.ERROR("This field is required. Please try again."))
                continue

            if not value and not required:
                return None

            if input_type == int:
                try:
                    return int(value)
                except ValueError:
                    self.stdout.write(self.style.ERROR("Please enter a valid number."))
                    continue

            return value

    def create_address_from_data(self, address_data):
        """Create address from provided data"""
        try:
            with transaction.atomic():
                # Create or get country
                country = self.get_or_create_country(address_data["country_name"], address_data.get("country_code", ""))

                # Create or get state
                state = self.get_or_create_state(address_data["state_name"], country)

                # Create or get city
                city = self.get_or_create_city(address_data["city_name"], state)

                # Create address
                address = self.create_address(
                    address_data["location"],
                    city,
                    address_data["zip_code"],
                    address_data.get("content_type"),
                    address_data.get("object_id"),
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully created address: {address.location}, " f"{city.name}, {state.name}, {country.name}"
                    )
                )

                return address

        except Exception as e:
            raise CommandError(f"Error creating address: {str(e)}")

    def get_or_create_country(self, name, code):
        """Get or create country"""
        if code:
            country, created = Country.objects.get_or_create(code=code, defaults={"name": name})
        else:
            # Generate code from name if not provided
            code = name.upper().replace(" ", "")[:10]
            country, created = Country.objects.get_or_create(name=name, defaults={"code": code})

        if created:
            self.stdout.write(f"Created country: {name} ({country.code})")
        else:
            self.stdout.write(f"Using existing country: {name} ({country.code})")

        return country

    def get_or_create_state(self, name, country):
        """Get or create state"""
        state, created = State.objects.get_or_create(name=name, country=country)

        if created:
            self.stdout.write(f"Created state: {name}, {country.name}")
        else:
            self.stdout.write(f"Using existing state: {name}, {country.name}")

        return state

    def get_or_create_city(self, name, state):
        """Get or create city"""
        city, created = City.objects.get_or_create(name=name, state=state)

        if created:
            self.stdout.write(f"Created city: {name}, {state.name}, {state.country.name}")
        else:
            self.stdout.write(f"Using existing city: {name}, {state.name}, {state.country.name}")

        return city

    def create_address(self, location, city, zip_code, content_type_name=None, object_id=None):
        """Create address"""
        # Set up content type and object_id if provided
        content_type = None
        if content_type_name and object_id:
            try:
                content_type = ContentType.objects.get(model=content_type_name)
            except ContentType.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Content type "{content_type_name}" not found. Using default.'))

        # Use default values if not provided
        if not content_type:
            content_type = ContentType.objects.first()  # Use first available content type
        if not object_id:
            object_id = 1  # Default object ID

        address = Address.objects.create(
            location=location,
            city=city,
            state=city.state,
            country=city.state.country,
            zip_code=zip_code,
            content_type=content_type,
            object_id=object_id,
        )

        return address

    def show_dry_run(self, address_data):
        """Show what would be created in dry run mode"""
        self.stdout.write(self.style.WARNING("DRY RUN - No data will be created"))
        self.stdout.write("Would create:")
        self.stdout.write(f'  Country: {address_data["country_name"]} ({address_data.get("country_code", "auto-generated")})')
        self.stdout.write(f'  State: {address_data["state_name"]}')
        self.stdout.write(f'  City: {address_data["city_name"]}')
        self.stdout.write(f'  Address: {address_data["location"]}, {address_data["zip_code"]}')

        if address_data.get("content_type"):
            self.stdout.write(f'  Content Type: {address_data["content_type"]}')
        if address_data.get("object_id"):
            self.stdout.write(f'  Object ID: {address_data["object_id"]}')

    def validate_address_data(self, address_data):
        """Validate address data using the address service"""
        validation_data = {
            "location": address_data["location"],
            "city_id": None,  # Will be set after city creation
            "zip_code": address_data["zip_code"],
        }

        # This would be called after city creation
        # result = self.address_service.validate_address(validation_data)
        # return result['is_valid']
        return True
