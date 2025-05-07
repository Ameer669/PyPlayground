import random

class GuessingGame:

    number = random.randint(1, 100)
    attempts = 0
    max_att = 10
    
    def __init__(self):
        self.Game()
        
    def Game(self):
        guess = None
        while guess != self.number and self.max_att > 0:
            guess = input(f"Guess a number between 1 and 100 (You have {self.max_att} attempts): ")
            if guess.isdigit():
                guess = int(guess)
                if guess > 100 or guess < 1:
                    print("\nEnter A Number Between 1 And 100!\n")
                else:
                    self.attempts += 1
                    self.max_att -= 1
                    if guess == self.number:
                        print(f"\nYou got it correct! You won in {self.attempts} attempts!\n")
                        return
                    elif guess > self.number:
                        print("\nLower!\n")
                    elif guess < self.number:
                        print("\nHigher!\n")
            else:
                print("Please enter a valid number.")
        if self.max_att == 0:
            print(f"Game over! The correct number was {self.number}\n.")


GuessingGame()

# The code above is a simple number-guessing game where the user has to guess a random number between 1 and 100.
# The user has a maximum of 10 attempts to guess the number. After each guess, the program provides feedback on whether the guess was too high or too low.
# If the user guesses the number correctly, they are congratulated and informed of the number of attempts taken. 
# If they run out of attempts, the game ends, revealing the correct number. 
# The game uses the random module to generate a random number and includes input validation to ensure the user enters a valid number within the specified range.
