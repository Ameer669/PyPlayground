import re
import secrets
import string

class PasswordChecker:
    def __init__(self):
        self.input()
        self.suggestion()
        if self.level != 4:
            self.generate()
            self.save()
        else:
            pass
            
    def input(self):
        self.password = input("\nEnter Your Password To check: ")
        self.has_digit = any(c.isdigit() for c in self.password)
        self.has_upper = any(c.isupper() for c in self.password)
        self.has_lower = any(c.islower() for c in self.password)
        self.has_char = any(c in '@$%&*!?' for c in self.password)
        self.level = self.has_digit + self.has_lower + self.has_upper + self.has_char
        self.length = len(self.password)
        if self.level == 4 and self.length >= 16:
            print("\n\033[1mYour password is very strong!\033[0m")
        elif self.level == 4 and self.length >= 8:
            print("\n\033[1mYour password is strong!\033[0m")
        elif self.level == 3 and self.length >= 8:
            print("\n\033[1mYour password is moderate!\033[0m")
        elif self.level == 2 and self.length >= 8:
            print("\n\033[1mYour password is weak!\033[0m")
        else:
            print("\n\033[1mYour password is very weak!\033[0m")
    
    def suggestion(self):
        
        if self.level == 4 and self.length >= 16:
            pass
        elif self.level == 3 or self.level == 2:
            print("")
            if self.length < 16:
                print("- Consider increasing the length of your password to 16 characters.")
            if not self.has_digit:
                print("- Consider adding digits to your password.")
            elif not self.has_upper:
                print("- Consider adding uppercase letters to your password.")
            elif not self.has_lower:
                print("- Consider adding lowercase letters to your password.")
            elif not self.has_char:
                print("- Consider adding special characters to your password.")
        else:
            if self.length < 8:
                print("- Password length must have 8 characters or more, consider increasing the length of your password, and adding digits, symbols, and characters.")
            elif self.length >= 16:
                print("- Password length alone is not enough! your password has to include digits, symbols, and characters.")
        print("")
    
    def generate(self, length=16):
        excluded_chars = ' "\'\\`}{[]()<>=:;,.?/~|/'  
        chars = string.ascii_letters + string.digits + ''.join(c for c in string.punctuation if c not in excluded_chars)
        
        while True:
            password = ''.join(secrets.choice(chars) for _ in range(length))
            if self.validate(password):
                self.password = password
                print(f"Suggested strong password: {password}\n")
                return password

    def save(self, filename=r"C:\Users\hp OMEN\Documents\Passwords.txt"):
        choice = input("Do you want to save the suggested password? (yes/no): ").strip().lower()
        if choice == 'no' or choice == 'n':
            print("Password not saved!")
            return
        elif choice == 'yes' or choice == 'y':
            if not self.password:
                print("No password to save.")
                return
            site = input("Enter the site or service name: ")
            with open(filename, "a") as file:
                file.write(f"{site}: {self.password}\n")
            print(f"\n\033[1mPassword saved to {filename}\033[0m")

    @staticmethod
    def validate(password):  
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$%&*!?]).{16,}$"
        return re.search(pattern, password, re.VERBOSE) is not None
    
def main():
    PasswordChecker()
    
     

if __name__ =="__main__":
    main()