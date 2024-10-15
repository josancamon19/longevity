import requests

headers = {
    'accept': 'application/json',
    'accept-language': 'en-US,en;q=0.9',
    'authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImFvNi1PYzAyQlZHTF9GbnBDeE5JMiJ9.eyJodHRwczovL2hlbGxvZnJlc2guY29tL2N1c3RvbWVyX3V1aWQiOiI2NTZlYTM4Mi02Y2Q2LTRmMGQtOWM4NS01ZjRiODg1ZDkxZDEiLCJodHRwczovL2hlbGxvZnJlc2guY29tL2NvdW50cnkiOiJmaiIsImh0dHBzOi8vaGVsbG9mcmVzaC5jb20vZW1haWwiOiJqb2FuLnNhbnRpYWdvLmNhYmV6YXNAZ21haWwuY29tIiwiaHR0cHM6Ly9oZWxsb2ZyZXNoLmNvbS91c2VybmFtZSI6ImpvYW4uc2FudGlhZ28uY2FiZXphc0BnbWFpbC5jb20iLCJpc3MiOiJodHRwczovL2ZhY3Rvcjc1LWxpdmUuZXUuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDY2ZWRiOTIwMGZlMmM4MGY5YmM0OTYzOCIsImF1ZCI6Imh0dHBzOi8vaGVsbG9mcmVzaC5jb20iLCJpYXQiOjE3Mjg5NjcxODAsImV4cCI6MTcyODk2ODk4MCwic2NvcGUiOiJvZmZsaW5lX2FjY2VzcyIsImd0eSI6WyJyZWZyZXNoX3Rva2VuIiwicGFzc3dvcmQiXSwiYXpwIjoiNGRpMGY0eHRyZ0dQcGRGS3dxSG1DWHNqVmtOZnJkbzIifQ.Aqy__T88K4NVJ9iIvP6eky1BusPm3t9bUc-5VCARvPVBaC9KqrH_0AE7SPuHUoaoLTGnlH2s2XpUhhmproh7w-cmINypqvkZMFZekNjm6airQWF-opvR6c7EPjkBAQYZNjKD_bGmjgH5-oPD0OZblji1PKumJVCTuqcJMYLGTXTJcXA4M-VQLzaLGfliSh_CQYSQPlwd1ELszAi_MVFkbdFpn_m92AiHFvHgNUJorcJSfOdanojFD7zQU1qmaYrzOtu8OUdxaVwfVbYo6LHRE4r7s_uIVPnd2uvfJRkjcG2PzyG1BBtgzPUc902zv_amswwvw1oOCWQXwpNdMr3Mew',
}

params = {
    'delivery-option': 'FJ-2-0800-2001',
    'postcode': '94114',
    'preference': 'caloriesmart',
    'product-sku': 'FJ-CBT8-18-1-0',
    'servings': '1',
    'subscription': '6987014',
    'week': '2024-W43',
    'include-future-feedback': 'true',
    'customerPlanId': '14e1a13f-70ec-47bf-82f4-21a7a62f5fbb',
    'country': 'US',
    'locale': 'en-US',
}


def get_addon_detail(addon_id: str):
    params = {'country': 'US', 'locale': 'en-US'}

    response = requests.get(
        f'https://www.factor75.com/gw/recipes/recipes/{addon_id}',
        params=params,
        headers=headers,
    )
    data = response.json()
    nutrition = data['nutrition']
    calories = protein = carbs = fat = 0
    for nutrient in nutrition:
        name = str(nutrient['name']).lower()
        if name == 'calories':
            calories = nutrient['amount']
        elif name == 'protein':
            protein = nutrient['amount']
        elif name == 'carbohydrate':
            carbs = nutrient['amount']
        elif name == 'fat':
            fat = nutrient['amount']

    return calories, protein, carbs, fat


def factor_meals_to_csv():
    response = requests.get('https://www.factor75.com/gw/my-deliveries/menu', params=params, headers=headers)
    data = response.json()
    meals = data['meals']
    items = []
    for meal in meals:
        quantity = meal.get('selection', {}).get('quantity', 0)
        if not quantity:
            continue
        recipe = meal['recipe']
        name = recipe['name']
        image = recipe['image']
        calories = recipe['nutrition']['calories']
        carbs = recipe['nutrition']['carbohydrate']
        protein = recipe['nutrition']['protein']
        fat = int((calories - (carbs + protein) * 4) / 9)
        print(name, quantity, calories, carbs, protein, fat)
        items.append({
            'name': name,
            'quantity': quantity,
            'calories': calories,
            'carbs': carbs,
            'protein': protein,
            'fat': fat,
            'image': image,
            'addon': False,
        })
    for group in data['addOns']['groups']:
        for option in group['addOns']:
            selection = option.get('selection', {})
            quantity = selection.get('oneOffQuantity', 0) + selection.get('preselectedQuantity', 0)
            if not quantity:
                continue
            recipe = option['recipe']
            recipe_id = option['recipe']['id']
            name = recipe['name']
            image = recipe['image']
            print(recipe_id, name, quantity)
            calories, protein, carbs, fat = get_addon_detail(recipe_id)
            items.append({
                'name': name,
                'quantity': quantity,
                'calories': calories,
                'carbs': carbs,
                'protein': protein,
                'fat': fat,
                'image': image,
                'addon': True,
            })
    # store in a csv
    import csv

    with open('meals2.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=items[0].keys())
        writer.writeheader()
        writer.writerows(items)


if __name__ == '__main__':
    factor_meals_to_csv()
