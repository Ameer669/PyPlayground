import random

class PasswordCheckerMaker:
    def __init__(self):
        self.call()
    
    def call(self):
        print("\nWelcome to Password Checker Maker\n")
        print("1. Check Password Strength")
        print("2. Generate Password")
        print("3. Exit")
        choice = input("\nEnter your choice: ")
        if choice == '1':
            self.input()
            self.suggestion()
        elif choice == '2':
            self.PasswordMaker()
        elif choice == '3':
            print("\nThank you for using Password Checker Maker!")
            exit()
        else:
            print("\nInvalid choice. Please try again.")
            self.call()
        print("")
        
    def input(self):
        password = input("\nEnter Your Password To check: ")
        self.has_digit = any(c.isdigit() for c in password)
        self.has_upper = any(c.isupper() for c in password)
        self.has_lower = any(c.islower() for c in password)
        self.has_char = any(c in '@$%&*!?' for c in password)
        self.level = self.has_digit + self.has_lower + self.has_upper + self.has_char
        self.length = len(password)
        if self.level == 4 and self.length >= 16:
            print("\nYour password is very strong!")
        elif self.level == 3 and self.length >= 8:
            print("\nYour password is strong.")
        elif self.level == 2 and self.length >= 8:
            print("\nYour password is weak.")
        else:
            print("\nYour password is very weak.")
    
    def suggestion(self):
        no = 1
        print("\n\nSuggestions to improve your password:")
        if self.level == 3 or self.level == 2:
            if self.length < 16:
                print(f"\n{no}) Consider increasing the length of your password to 16 characters.")
                no += 1 
            if not self.has_digit:
                print(f"\n{no}) Consider adding digits to your password.")
                no += 1
            elif not self.has_upper:
                print(f"\n{no}) Consider adding uppercase letters to your password.")
                no += 1
            elif not self.has_lower:
                print(f"\n{no}) Consider adding lowercase letters to your password.")
                no += 1
            elif not self.has_char:
                print(f"\n{no}) Consider adding special characters to your password.")
                no += 1
        else:
            print("\nYour password is too weak. Use at least 8 characters with a mix of letters, digits, and symbols.")
        
    def PasswordMaker(self):
        char = "%&$#@!~*?_-"
        num = "0123456789"
        lower = "abcdefghijklmnopqrstuvwxyz"
        upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        all = char + num + lower + upper
        length = 16
        while True:
            ran = input("Enter the number of the passwords: ")
            if ran.isdigit():
                ran = int(ran)
                for i in range(ran):
                    password = "".join(random.sample(all, length))
                    print("\n", password)
            else:
                print("\nPlease enter a valid number\n")
                continue
            break
            
    
PasswordCheckerMaker()
