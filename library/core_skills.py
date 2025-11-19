from random import random

random_list = random.randint(1, 21)

filtered_numbers = [n for n in random_list if n < 10]

filtered_by_filter = filter(lambda n: n < 10, filtered_numbers)
