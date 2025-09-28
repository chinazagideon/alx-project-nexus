#!/usr/bin/env python
"""
Simple script to populate address data manually.
This script can be run independently or imported into Django shell.
"""
import os
import sys

import django

# Add the project directory to Python path
sys.path.append("/Applications/MAMP/htdocs/alx-project-nexus")

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "job_portal.settings")
django.setup()

from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from address.models import Address, City, Country, State


def create_address_data(
    country_name, country_code, state_name, city_name, location, zip_code, content_type_name=None, object_id=None
):
    """
    Create address data with proper relationships.

    Args:
        country_name (str): Name of the country
        country_code (str): Country code (e.g., 'US', 'CA')
        state_name (str): Name of the state/province
        city_name (str): Name of the city
        location (str): Street address
        zip_code (str): ZIP/postal code
        content_type_name (str, optional): Content type for the address
        object_id (int, optional): Object ID for the address relationship

    Returns:
        Address: Created address object
    """
    try:
        with transaction.atomic():
            # Create or get country
            country, country_created = Country.objects.get_or_create(code=country_code, defaults={"name": country_name})
            print(f"{'Created' if country_created else 'Found'} country: {country.name} ({country.code})")

            # Create or get state
            state, state_created = State.objects.get_or_create(name=state_name, country=country)
            print(f"{'Created' if state_created else 'Found'} state: {state.name}, {country.name}")

            # Create or get city
            city, city_created = City.objects.get_or_create(name=city_name, state=state)
            print(f"{'Created' if city_created else 'Found'} city: {city.name}, {state.name}, {country.name}")

            # Set up content type and object_id
            if content_type_name and object_id:
                try:
                    content_type = ContentType.objects.get(model=content_type_name)
                except ContentType.DoesNotExist:
                    print(f"Warning: Content type '{content_type_name}' not found. Using default.")
                    content_type = ContentType.objects.first()
            else:
                content_type = ContentType.objects.first()
                object_id = 1

            # Create address
            address = Address.objects.create(
                location=location,
                city=city,
                state=city.state,
                country=city.state.country,
                zip_code=zip_code,
                content_type=content_type,
                object_id=object_id,
            )

            print(f"Created address: {address.location}, {city.name}, {state.name}, {country.name}")
            return address

    except Exception as e:
        print(f"Error creating address: {str(e)}")
        raise


def create_sample_addresses():
    """Create some sample addresses for testing"""
    sample_addresses = [
        {
            "country_name": "United States",
            "country_code": "US",
            "state_name": "California",
            "city_name": "San Francisco",
            "location": "123 Market Street",
            "zip_code": "94102",
            "content_type_name": "user",
            "object_id": 1,
        },
        {
            "country_name": "United States",
            "country_code": "US",
            "state_name": "New York",
            "city_name": "New York City",
            "location": "456 Broadway",
            "zip_code": "10013",
            "content_type_name": "company",
            "object_id": 1,
        },
        {
            "country_name": "Canada",
            "country_code": "CA",
            "state_name": "Ontario",
            "city_name": "Toronto",
            "location": "789 Bay Street",
            "zip_code": "M5G 1M5",
            "content_type_name": "user",
            "object_id": 2,
        },
    ]

    print("Creating sample addresses...")
    for addr_data in sample_addresses:
        create_address_data(**addr_data)
        print("-" * 50)


def interactive_create():
    """Interactive mode to create address data"""
    print("=== Interactive Address Creation ===")

    country_name = input("Enter country name: ").strip()
    country_code = input("Enter country code (e.g., US): ").strip()
    state_name = input("Enter state/province name: ").strip()
    city_name = input("Enter city name: ").strip()
    location = input("Enter street address: ").strip()
    zip_code = input("Enter ZIP/postal code: ").strip()

    content_type_name = input("Enter content type (optional): ").strip() or None
    object_id = input("Enter object ID (optional): ").strip()
    object_id = int(object_id) if object_id.isdigit() else None

    create_address_data(
        country_name=country_name,
        country_code=country_code,
        state_name=state_name,
        city_name=city_name,
        location=location,
        zip_code=zip_code,
        content_type_name=content_type_name,
        object_id=object_id,
    )


def show_existing_addresses():
    """Show existing addresses in the database"""
    addresses = Address.objects.select_related("city__state__country").all()

    print(f"\n=== Existing Addresses ({addresses.count()}) ===")
    for addr in addresses:
        print(f"ID: {addr.id}")
        print(f"Location: {addr.location}")
        print(f"City: {addr.city.name}")
        print(f"State: {addr.city.state.name}")
        print(f"Country: {addr.city.state.country.name} ({addr.city.state.country.code})")
        print(f"ZIP: {addr.zip_code}")
        print(f"Content Type: {addr.content_type}")
        print(f"Object ID: {addr.object_id}")
        print("-" * 50)


if __name__ == "__main__":
    print("Address Population Script")
    print("1. Create sample addresses")
    print("2. Interactive address creation")
    print("3. Show existing addresses")
    print("4. Exit")

    while True:
        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            create_sample_addresses()
        elif choice == "2":
            interactive_create()
        elif choice == "3":
            show_existing_addresses()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
