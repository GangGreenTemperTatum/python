import random

print("Hello and welcome to the Magic 8 Ball\n")

name = input('Please enter your name: ')
# print(name)

if name == "":
    print("You didn't enter a name, so I'll call you Bob")
    name = "Bob"

question = input('Enter your question: ')

if question == "":
    print("You didn't enter a question, so I'll ask you one")
    question = input("Do you think you'll study Python today? ")

print(name + " asks: " + question)

# placeholder answer var
answer = ""

random_number = random.randint(1, 9)
# print(random_number)

if random_number == 1:
    answer = "Yes - definitely"
elif random_number == 2:
    answer = "It is decidedly so"
elif random_number == 3:
    answer = "Without a doubt"
elif random_number == 4:
    answer = "Reply hazy, try again"
elif random_number == 5:
    answer = "Ask again later"
elif random_number == 6:
    answer = "Better not tell you now"
elif random_number == 7:
    answer = "My sources say no"
elif random_number == 8:
    answer = "Outlook not so good"
elif random_number == 9:
    answer = "Very doubtful"
else:
    print("oh dear, error, beep boop")

print("\nMagic 8-Ball's answer: " + answer)
