import random

weight = random.randint(1, 100)
print("Welcome to the Shipping Accounts Program 🚚")
print("Please note, we don't accept coins and only round up the nearest full dollar 🤑\n")
weight = 8.4

lb_cost_ground = 0.00
lb_cost_premium = 0.00
flat_charge = round(20.00)
total_price_ground = 0.00
total_price_premium = 0.00

print("Ok, your weight totals at " + str(weight) + "lbs")

if weight <= 2:
    lb_cost_ground = 1.50
    lb_cost_premium = 4.50
    total_price_ground = round(lb_cost_ground * weight + flat_charge)
    total_price_premium = round(lb_cost_premium * weight + flat_charge)
    print("\nPrice per lb is $" + str(lb_cost_ground) +
          " for ground shipping, " + "or premium shipping is $" + str(round(lb_cost_premium)) + " per-lbs with flat charge: $" + str(flat_charge))
    print("\nWhich equals either $" + str(round(lb_cost_ground * weight)) +
          " for ground or $" + str(round(lb_cost_premium * weight)) + " for premium")
    print("\nPlus flat charge of $" + str(flat_charge) +
          " equals a total of $" + str(total_price_ground) + " or $" + str(total_price_premium))
elif weight > 2 and weight <= 6:
    lb_cost_ground = 1.50
    lb_cost_premium = 4.50
    total_price_ground = round(lb_cost_ground * weight + flat_charge)
    total_price_premium = round(lb_cost_premium * weight + flat_charge)
    print("\nPrice per lb is $" + str(lb_cost_ground) +
          " for ground shipping, " + "or premium shipping is $" + str(round(lb_cost_premium)) + " per-lbs with flat charge: $" + str(flat_charge))
    print("\nWhich equals either $" + str(round(lb_cost_ground * weight)) +
          " for ground or $" + str(round(lb_cost_premium * weight)) + " for premium")
    print("\nPlus flat charge of $" + str(flat_charge) +
          " equals a total of $" + str(total_price_ground) + " or $" + str(total_price_premium))
elif weight > 6 and weight <= 10:
    lb_cost_ground = 1.50
    lb_cost_premium = 4.50
    total_price_ground = round(lb_cost_ground * weight + flat_charge)
    total_price_premium = round(lb_cost_premium * weight + flat_charge)
    print("\nPrice per lb is $" + str(lb_cost_ground) +
          " for ground shipping, " + "or premium shipping is $" + str(round(lb_cost_premium)) + " per-lbs with flat charge: $" + str(flat_charge))
    print("\nWhich equals either $" + str(round(lb_cost_ground * weight)) +
          " for ground or $" + str(round(lb_cost_premium * weight)) + " for premium")
    print("\nPlus flat charge of $" + str(flat_charge) +
          " equals a total of $" + str(total_price_ground) + " or $" + str(total_price_premium))
else:
    lb_cost_ground = 1.50
    lb_cost_premium = 4.50
    total_price_ground = round(lb_cost_ground * weight + flat_charge)
    total_price_premium = round(lb_cost_premium * weight + flat_charge)
    print("\nPrice per lb is $" + str(lb_cost_ground) +
          " for ground shipping, " + "or premium shipping is $" + str(round(lb_cost_premium)) + " per-lbs with flat charge: $" + str(flat_charge))
    print("\nWhich equals either $" + str(round(lb_cost_ground * weight)) +
          " for ground or $" + str(round(lb_cost_premium * weight)) + " for premium")
    print("\nPlus flat charge of $" + str(flat_charge) +
          " equals a total of $" + str(total_price_ground) + " or $" + str(total_price_premium))

customer_shipping_preference = input(
    '\nWould you like to ship via ground or premium? ')
customer_shipping_preference_lower = customer_shipping_preference.lower()

print("\n\n\nOk, beep boop, calculating...\n\n\n")

if customer_shipping_preference_lower == "ground":
    print("Ok, your total shipping cost is $" + str(total_price_ground))
elif customer_shipping_preference_lower == "premium":
    print("Ok, your total shipping cost is $" + str(total_price_premium))
else:
    print("Sorry, we don't have that option, please try again")
