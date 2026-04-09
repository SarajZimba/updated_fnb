# from decimal import Decimal
# from collections import defaultdict

# def adjust_item_current_level_after_sale(recipe_name, sold_qty, outlet, cursor, mydb, order_date):
#     # Step 1: Get recipe ID
#     cursor.execute("""
#         SELECT id FROM recipe WHERE name = %s AND outlet = %s
#     """, (recipe_name, outlet))
#     recipe_row = cursor.fetchone()
#     if not recipe_row:
#         print(f"Recipe not found: {recipe_name}")
#         return

#     recipe_id = recipe_row[0]

#     # Step 2: Initialize ingredient aggregator
#     aggregated_ingredients = defaultdict(float)

#     # Step 3: Add direct ingredients
#     cursor.execute("""
#         SELECT name, quantity FROM recipe_items WHERE recipe_id = %s
#     """, (recipe_id,))
#     direct_ingredients = cursor.fetchall()

#     for name, qty in direct_ingredients:
#         aggregated_ingredients[name] += float(Decimal(qty) * Decimal(sold_qty))

#     # Step 4: Process sub-recipes
#     cursor.execute("""
#         SELECT sr.id, rs.quantity
#         FROM recipe_subrecipes rs
#         JOIN sub_recipe sr ON rs.sub_recipe_id = sr.id
#         WHERE rs.recipe_id = %s
#     """, (recipe_id,))
#     sub_recipes = cursor.fetchall()

#     for sub_recipe_id, sub_recipe_qty in sub_recipes:
#         # Get sub-recipe ingredients
#         cursor.execute("""
#             SELECT name, quantity FROM sub_recipe_items WHERE sub_recipe_id = %s
#         """, (sub_recipe_id,))
#         sub_items = cursor.fetchall()

#         for item_name, item_qty in sub_items:
#             total_sub_qty = float(Decimal(sub_recipe_qty) * Decimal(item_qty) * Decimal(sold_qty))
#             aggregated_ingredients[item_name] += total_sub_qty

#     # Step 5: Decrease from inventory & insert into consumption tracker
#     for ingredient_name, total_to_decrease in aggregated_ingredients.items():
#         while total_to_decrease > 0:
#             cursor.execute("""
#                 SELECT id, quantity, rate FROM item_current_level
#                 WHERE itemname = %s AND outlet = %s AND quantity > 0
#                 ORDER BY id ASC LIMIT 1
#             """, (ingredient_name, outlet))
#             stock_row = cursor.fetchone()

#             if stock_row:
#                 item_id, current_qty, rate = stock_row

#                 if current_qty >= total_to_decrease:
#                     new_qty = float(current_qty) - total_to_decrease

#                     # Update stock
#                     cursor.execute("""
#                         UPDATE item_current_level SET quantity = %s WHERE id = %s
#                     """, (new_qty, item_id))
#                     mydb.commit()

#                     # Track consumption
#                     cursor.execute("""
#                         INSERT INTO consumption_tracker (item_name, consumed_quantity, rate, outlet, recipe_name, order_date)
#                         VALUES (%s, %s, %s, %s, %s, %s)
#                     """, (ingredient_name, total_to_decrease, rate, outlet, recipe_name, order_date))
#                     mydb.commit()

#                     total_to_decrease = 0

#                 else:
#                     # Consume all available and continue
#                     cursor.execute("""
#                         UPDATE item_current_level SET quantity = 0 WHERE id = %s
#                     """, (item_id,))
#                     mydb.commit()

#                     # Track partial consumption
#                     cursor.execute("""
#                         INSERT INTO consumption_tracker (item_name, consumed_quantity, rate, outlet, recipe_name, order_date)
#                         VALUES (%s, %s, %s, %s, %s, %s)
#                     """, (ingredient_name, current_qty, rate, outlet, recipe_name, order_date))
#                     mydb.commit()

#                     total_to_decrease -= float(current_qty)
#             else:
#                 print(f"Not enough stock to deduct for ingredient: {ingredient_name} in outlet {outlet}")
#                 break

from decimal import Decimal
from collections import defaultdict

def adjust_item_current_level_after_sale(recipe_name, sold_qty, outlet, cursor, mydb, order_date):
    # Step 1: Get recipe ID
    cursor.execute("""
        SELECT id FROM recipe WHERE name = %s AND outlet = %s
    """, (recipe_name, outlet))
    recipe_row = cursor.fetchone()
    if not recipe_row:
        print(f"Recipe not found: {recipe_name}")
        return

    recipe_id = recipe_row[0]

    # Step 2: Initialize ingredient aggregator
    aggregated_ingredients = defaultdict(float)

    # Step 3: Add direct ingredients
    cursor.execute("""
        SELECT name, quantity FROM recipe_items WHERE recipe_id = %s
    """, (recipe_id,))
    direct_ingredients = cursor.fetchall()

    for name, qty in direct_ingredients:
        aggregated_ingredients[name] += float(Decimal(qty) * Decimal(sold_qty))

    # Step 4: Process sub-recipes
    cursor.execute("""
        SELECT sr.id, rs.quantity
        FROM recipe_subrecipes rs
        JOIN sub_recipe sr ON rs.sub_recipe_id = sr.id
        WHERE rs.recipe_id = %s
    """, (recipe_id,))
    sub_recipes = cursor.fetchall()

    for sub_recipe_id, sub_recipe_qty in sub_recipes:
        # Get sub-recipe ingredients
        cursor.execute("""
            SELECT name, quantity FROM sub_recipe_items WHERE sub_recipe_id = %s
        """, (sub_recipe_id,))
        sub_items = cursor.fetchall()

        for item_name, item_qty in sub_items:
            total_sub_qty = float(Decimal(sub_recipe_qty) * Decimal(item_qty) * Decimal(sold_qty))
            aggregated_ingredients[item_name] += total_sub_qty

    # Step 5: Decrease from inventory & insert into consumption tracker
    for ingredient_name, total_to_decrease in aggregated_ingredients.items():
        while total_to_decrease > 0:
            cursor.execute("""
                SELECT id, quantity, rate FROM item_current_level
                WHERE itemname = %s AND outlet = %s AND quantity > 0
                ORDER BY id ASC LIMIT 1
            """, (ingredient_name, outlet))
            stock_row = cursor.fetchone()

            if stock_row:
                item_id, current_qty, rate = stock_row

                if current_qty >= total_to_decrease:
                    new_qty = float(current_qty) - total_to_decrease

                    # Update stock
                    cursor.execute("""
                        UPDATE item_current_level SET quantity = %s WHERE id = %s
                    """, (new_qty, item_id))
                    mydb.commit()

                    # Track consumption
                    cursor.execute("""
                        INSERT INTO consumption_tracker (item_name, consumed_quantity, rate, outlet, recipe_name, order_date)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (ingredient_name, total_to_decrease, rate, outlet, recipe_name, order_date))
                    mydb.commit()

                    total_to_decrease = 0

                else:
                    # Consume all available and continue
                    cursor.execute("""
                        UPDATE item_current_level SET quantity = 0 WHERE id = %s
                    """, (item_id,))
                    mydb.commit()

                    # Track partial consumption
                    cursor.execute("""
                        INSERT INTO consumption_tracker (item_name, consumed_quantity, rate, outlet, recipe_name, order_date)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (ingredient_name, current_qty, rate, outlet, recipe_name, order_date))
                    mydb.commit()

                    total_to_decrease -= float(current_qty)
            else:
                print(f"Not enough stock to deduct for ingredient: {ingredient_name} in outlet {outlet}")
                break