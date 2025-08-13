"""
- Description: Text-based Pig game
- How to play:
  1. Players take turns rolling a die.
  2. On each turn, a player can roll the die as many times as they want, accumulating points for each roll.
  3. If a player rolls a 1, they lose all points for that turn and their turn ends.
  4. If a player chooses to "hold", their turn ends and their turn points are added to their total score.
  5. The first player to reach the winning score (default 100) wins the game.
"""

import random as rnd
import time

class Player:
    def __init__(self):
        self.score = 0
        self.turn_score = 0
        self.is_round_complete = False

class PIG:
    def __init__(self):
        self.win_score = 100

    def take_turn(self, player, player_num):
        player.turn_score = 0
        player.is_round_complete = False
        print(f"\033[1m\nPlayer {player_num}'s turn\033[0m")
        while not player.is_round_complete:
            print(f"Current score: {player.score}, Turn score: {player.turn_score}")
            choice = input("(R)oll again or (H)old? ").strip().lower()
            if choice == 'r':
                dice = rnd.randint(1, 6)
                time.sleep(0.5)
                for char in f"You rolled a {dice}":
                    print(char, end='', flush=True)
                    time.sleep(0.05)
                print("\n")
                if dice == 1:
                    player.turn_score = 0
                    player.is_round_complete = True
                    print("\033[31mRound over! You rolled a 1.\033[0m")
                else:
                    player.turn_score += dice
                    if player.score + player.turn_score >= self.win_score:
                        print(f"\033[1m\nCongratulations! Player {player_num} won!\033[0m\n")
                        return True
            elif choice == 'h':
                player.score += player.turn_score
                player.turn_score = 0
                player.is_round_complete = True
                print("\033[33m\nYou held. Turn score added to total.\033[0m")
            else:
                print("Invalid choice. Please enter 'R' or 'H'.")
        print(f"Total score for Player {player_num}: {player.score}")
        if player.score >= self.win_score:
            print(f"\033[1m\nCongratulations! Player {player_num} won!\033[0m\n")
            return True
        return False

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

        current_player = 0
        while True:
            if self.take_turn(players[current_player], current_player + 1):
                break
            current_player = (current_player + 1) % num_players

def main():
    PIG().start_game()

if __name__ == "__main__":
    main()
