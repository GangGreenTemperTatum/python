import itertools

# Given string
input_string = "ABCDEFG"

# Generate all permutations
permutations = [''.join(p) for p in itertools.permutations(input_string)]

# Print the total number of permutations and the permutations themselves
print(f"Total permutations: {len(permutations)}")
for perm in permutations:
    print(perm)

