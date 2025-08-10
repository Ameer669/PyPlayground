import random
import time

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
        print("You will be asked 10 questions.\nYou have 20 seconds to solve them all.\nRespond as quickly and accurately as possible.\n")
        input("Press Enter to start...")
        print("\n")
        time.sleep(1)

        correct = 0
        start_time = time.time()
        for i in range(10):
            self.eq()
            while True:
                try:
                    ans = float(input(f"{i+1}. What is {self.p}? "))
                    break
                except ValueError:
                    print("\033[31mInvalid input! Please enter a number.\n\033[0m")
                    continue
            if ans == self.val:
                correct += 1
                print("\033[32mCorrect!\n\033[0m")
            else:
                print("\033[31mFalse!\n\033[0m")
                print(f"The correct answer was {self.val}.\n")
        end_time = time.time()
        self.total_time = end_time - start_time
        self.correct = correct


    def result(self):
        self.handle()
        
        fast_correct = [
            "Your brain is a calculator on rocket fuel!",
            "A true math gladiator — flawless victory!",
            "Numbers fear you — you're that fast!",
            "Blazing speed and sharp mind — you crushed it!"
        ]
        slow_correct = [
            "Decent work, but you've got another gear to find!",
            "Close call! Speed's good, but aim for perfection!",
            "Slow and steady didn't win this race — push harder!",
            "Quick reflexes, but your aim was off — practice!"
        ]
        fast_wrong = [
            "Lightning fast, but accuracy is your next quest!",
            "Speed demon, but the answers slipped through!",
            "Speed like lightning, but accuracy like a storm — chaotic!",
            "Epic fail speedrun — wrong answers at record pace!"
        ]
        slow_wrong = [
            "Both slow and wrong — the ultimate double whammy!",
            "Math is weeping... and so should you — train more!",
            "Slow and steady didn't win this race — push harder!",
            "You fought bravely, but the math boss remains undefeated!"
        ]
        if self.total_time < 20 and self.correct >= 5:
            time.sleep(1)
            print(f"You answered \033[32m{int(self.correct)} out of 10\033[0m questions and took \033[32m{self.total_time:.2f}\033[0m seconds.")
            time.sleep(1)
            print(f"\033[1m\n{random.choice(fast_correct)}\033[0m\n")
        elif self.total_time > 20 and self.correct >= 5:
            time.sleep(1)
            print(f"You answered \033[32m{int(self.correct)} out of 10\033[0m questions but took \033[31m{self.total_time:.2f}\033[0m seconds.")
            time.sleep(1)
            print(f"\033[1m\n{random.choice(slow_correct)}\033[0m\n")
        elif self.correct < 5 and self.total_time < 20:
            time.sleep(1)
            print(f"You answered \033[31m{int(self.correct)} out of 10\033[0m questions and took \033[32m{self.total_time:.2f}\033[0m seconds.")
            time.sleep(1)
            print(f"\033[1m\n{random.choice(fast_wrong)}\033[0m\n")
        else:
            time.sleep(1)
            print(f"You answered \033[31m{int(self.correct)} out of 10\033[0m questions and took \033[31m{self.total_time:.2f}\033[0m seconds.")
            time.sleep(1)
            print(f"\033[1m\n{random.choice(slow_wrong)}\033[0m\n")


if __name__ == "__main__":
    mc = MathChallenge()
    mc.result()