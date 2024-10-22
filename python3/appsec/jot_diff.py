import base64
import os

# Get the encoded strings from environment variables
JWT_TOKEN1 = os.environ.get('JWT_TOKEN1')
JWT_TOKEN2 = os.environ.get('JWT_TOKEN2')

# Ensure both tokens are retrieved
if JWT_TOKEN1 is None or JWT_TOKEN2 is None:
    print("One or both JWT tokens are not set in the environment.")
else:
    # Decode the strings
    decoded1 = base64.b64decode(JWT_TOKEN1).decode('utf-8')
    decoded2 = base64.b64decode(JWT_TOKEN2).decode('utf-8')

    print("Decoded String 1:")
    print(decoded1)

    print("\nDecoded String 2:")
    print(decoded2)

    # Compare
    if decoded1 != decoded2:
        print("\nThe strings differ!")
    else:
        print("\nThe strings are identical.")
