import random as rnd
import time

class Player:
    def __init__(self):
        self.score = 0
        self.turn_score = 0
        self.is_round_complete = False

class PIG:
    def __init__(self):
        self.score = 0
        self.turn_score = 0
        self.is_round_complete = False
        self.is_game_over = False
        self.dice = rnd.randint(1, 6)
        self.win_score = 100

    def roll(self):
        if self.dice == 1:
            self.turn_score = 0
            self.is_round_complete = True
        elif self.dice in range(2,7):
            self.turn_score += self.dice
        
    def hold(self):
        self.score += self.turn_score 
        self.turn_score = 0
        
    def start_game(self):
        while True:
            try:
                num_players = int(input("Enter number of players: "))
                if num_players < 1:
                    print("Enter a valid number!\n")
                    continue
                players = [Player() for _ in range(num_players)]
                break
            except ValueError:
                print("Enter a valid number!\n")
        is_game_over = False
        current_player = 0

        while not is_game_over:
            player = players[current_player]
            player.turn_score = 0
            player.is_round_complete = False
            print(f"\033[1m\nPlayer {current_player + 1}'s turn\033[0m")
            while not player.is_round_complete:
                print(f"Current score: {player.score}, Turn score: {player.turn_score}")
                choice = input("(R)oll again or (H)old? ").strip().lower()
                if choice == 'r':
                    dice = rnd.randint(1, 6)
                    time.sleep(0.5)
                    for char in f"You rolled a {dice}":
                        print(char, end='', flush=True)
                        time.sleep(0.05)
                    time.sleep(0.5)
                    print("\n")
                    if dice == 1:
                        player.turn_score = 0
                        player.is_round_complete = True
                        print("Round over! You rolled a 1.")
                    else:
                        player.turn_score += dice
                        if player.turn_score + player.score >= self.win_score:
                            print(f"\033[1m\nCongratulations! Player {current_player + 1} won!\033[0m\n")
                            is_game_over = True
                            exit()
                elif choice == 'h':
                    player.score += player.turn_score
                    player.turn_score = 0
                    player.is_round_complete = True
                    print("You held. Turn score added to total.")
                else:
                    print("Invalid choice. Please enter 'R' or 'H'.\n")
            print(f"Total score for Player {current_player + 1}: {player.score}")
            if player.score >= self.win_score:
                print(f"\033[1m\nCongratulations! Player {current_player + 1} won!\033[0m\n")
                is_game_over = True
            else:
                current_player = (current_player + 1) % num_players


    def game(self):
        while not self.is_game_over:
            self.is_round_complete = False
            self.turn_score = 0 
            print(f"Current score: {self.score}, Turn score: {self.turn_score}")
            while not self.is_round_complete:
                choice = input("(R)oll again or (H)old? ").strip().lower()
                if choice == 'r':
                    self.dice = rnd.randint(1, 6)
                    print(f"You rolled a {self.dice}")
                    self.roll()
                    if self.is_round_complete:
                        print("Round over! You rolled a 1.")
                elif choice == 'h':
                    self.hold()
                    print("You held. Turn score added to total.")
                else:
                    print("Invalid choice. Please enter 'R' or 'H'.")
            print(f"Total score: {self.score}")
            if self.score >= self.win_score:
                print("\033[1m\nCongratulations! You won!\033[0m\n")
                self.is_game_over = True
                break

def main():
    Pig = PIG()
    Pig.start_game()
    Pig.game()
    
if __name__ == "__main__":
    main()