import random
import json

# Generate a list of random numbers 
num_random_numbers = 500  
min_value = 1000  
max_value = 9999  

random_numbers = random.sample(range(min_value, max_value), num_random_numbers)

# Save the numbers to a JSON file
with open('numbers.json', 'w') as f:
    json.dump(random_numbers, f)

print(f"{num_random_numbers} random numbers generated and saved to 'numbers.json'.")
