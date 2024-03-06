# import requests
# import mysql.connector
# import pandas as pd

# create a function
def caeser_encrypt(plaintext, offset):
    # set encryption text empty var
    encrypt_text = ""
    # for loop to iterate each input character
    for character in plaintext:
        # identify upper or lower
        is_uppercase = character.isupper()
        is_alpha = character.isalpha()
        # then convert the character to ascii
        character_code = ord(character)
        # apply the given offset
        new_character_code = character_code + offset
        # store the value as ciphertext var and convert back to character
        encrypt_text += chr(new_character_code)
        # return result
    #return plaintext
    #return offset
    return encrypt_text
# create an input prompt:
#plaintext = input("Enter text to cipher!:")
#offset = input("Enter the offset shift of each character:")
# test with pre-determined values
print(caeser_encrypt("The world is not enough", 2))
