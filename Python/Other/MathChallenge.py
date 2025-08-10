import random

class MathChallenge:
    def __init__(self):
        self.operators  = ['-', '+', '*', '/']
        self.numbers = list(range(1,11))
        
        
    def eq(self):
        while True:
            no1 = random.choice(self.numbers)
            no2 = random.choice(self.numbers)
            op = random.choice(self.operators)
            if op == '/':
                if no2 == 0:
                    continue
                if no1 % no2 != 0:
                    continue
            if no1 < no2:
                continue
            self.p = f"{no1} {op} {no2}"
            self.val = eval(self.p)
            self.val = round(self.val, 2)
            break

    def handle(self):
        print("\033[1mWelcome to the Math Challenge!\n\033[0m")
        print("You will be asked 10 questions,\nanswer as many as you can!\n")
        co = 0
        for i in range(10):
            self.eq()
            c = float(input(f"{i+1}. What is {self.p}? "))
            if c == self.val:
                co += 1
                print("\033[32mCorrect!\n\033[0m")
            else:
                print("\033[31mFalse!\n\033[0m")
                print(f"The correct answer was {self.val}.\n")
        print(f"You got {co} out of 10 questions correct!\n")


if __name__ == "__main__":
    mc = MathChallenge()
    mc.handle()