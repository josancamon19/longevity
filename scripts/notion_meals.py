import csv
import json
import os

import requests

# Notion API setup
NOTION_VERSION = '2022-06-28'
HEADERS = {
    "Authorization": f"Bearer {os.getenv('NOTION_SECRET')}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION
}


def read_meals_from_csv(filename):
    meals_data = []
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            meals_data.append({
                "name": row['name'],
                "quantity": int(row['quantity']),
                "calories": int(row['calories']),
                "carbs": int(row['carbs']),
                "protein": int(row['protein']),
                "fat": int(row['fat']),
                "image": row['image'],
                "addon": row['addon'].lower() == 'true'
            })
    return meals_data


def create_meals_database(parent_page_id, meals_data):
    create_url = "https://api.notion.com/v1/databases"

    payload = {
        "parent": {"page_id": parent_page_id},
        "title": [{"type": "text", "text": {"content": "Meals Database"}}],
        "properties": {
            "Name": {"title": {}},
            "Calories": {"number": {"format": "number"}},
            "Carbs": {"number": {"format": "number"}},
            "Protein": {"number": {"format": "number"}},
            "Fat": {"number": {"format": "number"}},
            "Image": {"files": {}},
            "Addon": {"checkbox": {}}
        }
    }

    response = requests.post(create_url, headers=HEADERS, json=payload)
    return response.json()


def create_consumption_database(parent_page_id, meals_database_id):
    create_url = "https://api.notion.com/v1/databases"

    payload = {
        "parent": {"page_id": parent_page_id},
        "title": [{"type": "text", "text": {"content": "Daily Consumption"}}],
        "properties": {
            "Name": {"title": {}},
            "Date": {"date": {}},
            "Meal": {"relation": {"database_id": meals_database_id, "single_property": {}}},
            "Quantity": {"number": {"format": "number"}},
            # "Calories": {"formula": {"expression": "prop(\"Quantity\") * prop(\"Meal\").at(0).prop(\"Calories\")"}},
        }
    }

    response = requests.post(create_url, headers=HEADERS, json=payload)
    return response.json()


def add_meals_to_database(database_id, meals_data):
    create_url = "https://api.notion.com/v1/pages"

    for meal in meals_data:
        payload = {
            "parent": {"database_id": database_id},
            "properties": {
                "Name": {"title": [{"text": {"content": meal["name"]}}]},
                "Calories": {"number": meal["calories"]},
                "Carbs": {"number": meal["carbs"]},
                "Protein": {"number": meal["protein"]},
                "Fat": {"number": meal["fat"]},
                "Image": {"files": [{"type": "external", "name": "Meal Image", "external": {"url": meal["image"]}}]},
                "Addon": {"checkbox": meal["addon"]},
            }
        }

        response = requests.post(create_url, headers=HEADERS, json=payload)
        if response.status_code != 200:
            print(f"Failed to add meal: {meal['name']}")
            print(response.text)


def print_database_fields(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}"
    response = requests.get(url, headers=HEADERS)
    database = response.json()
    print(json.dumps(database, indent=2))


# Main execution
if __name__ == "__main__":

    csv_filename = 'meals.csv'
    meals_data = read_meals_from_csv(csv_filename)

    parent_page_id = '12068483e9e880b183e9e7c505fce983'

    # Create Meals Database
    meals_result = create_meals_database(parent_page_id, meals_data)
    if 'id' in meals_result:
        print("Meals Database created successfully!")
        meals_database_id = meals_result['id']
        add_meals_to_database(meals_database_id, meals_data)
        print("Meals added to the database.")

        # Create Consumption Database
        consumption_result = create_consumption_database(parent_page_id, meals_database_id)
        if 'id' in consumption_result:
            print("Consumption Database created successfully!")
        else:
            print("Failed to create Consumption Database:")
            print(json.dumps(consumption_result, indent=2))
    else:
        print("Failed to create Meals Database:")
        print(json.dumps(meals_result, indent=2))
