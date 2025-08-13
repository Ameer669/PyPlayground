"""
Authored by: Ameer669
Date: 13/08/2025
Game logic by: Ameer669
Description: Text-based Blackjack game (Without Betting "Haram")

support:
- Multiple players vs. a dealer (the House)
- Split, double down, natural blackjack detection
- Points tracking for players and the House across multiple rounds

How points work (per player per round):
- Player win: +1 point (or +2 if double-down win or natural blackjack)
- Push: 0 points
- Player loss: 0 points (or -1 if double-down loss)
 - House (Dealer): gains +1 point for each player loss; loses points when players win (-1 normal win, -2 double-down win); push is 0

 Features:
- Basic game loop with player input for actions (hit, stand, double down, split)
- A simple colored text-based UI for displaying hands and results (using ANSI escape codes)
- Error handling for invalid inputs
- Support for multiple players and rounds

Use: Run main(); set number of players and rounds; follow prompts.
"""

import random
import time

# -----------------------------------------------------------------------------
# Core deck abstraction
# -----------------------------------------------------------------------------
class Deck:
    """A single shared deck of cards (52-card standard deck).

    Responsibilities:
    - Maintain a shuffled list of remaining (rank, suit) tuples.
    - Provide a draw() method that returns a (rank, suit) tuple.
    - Reset (reshuffle to full 52 cards) when empty or when explicitly requested.
    """
    def __init__(self, ranks, suits):
        self.ranks = ranks
        self.suits = suits
        self.reset()

    def reset(self):
        """Fill the deck with 52 cards and shuffle."""
        self._deck = [(r, s) for r in self.ranks for s in self.suits]
        random.shuffle(self._deck)

    def draw(self):
        """Pop and return a single (rank, suit) tuple; reset deck if empty."""
        if not self._deck:
            self.reset()
        return self._deck.pop()

    def remaining(self):
        """Return number of cards left in the deck."""
        return len(self._deck)

# -----------------------------------------------------------------------------
# Player, Dealer, Hand
# -----------------------------------------------------------------------------
class Player:
    """A participant in the game with a hand and running points.

    Attributes:
        name: Display name of the player.
        hand: The player's Hand instance.
        points: Accumulated points across rounds.
        turn_over: Whether the player's turn has ended for the current hand.
        doubled_down: Whether the player doubled down for this hand.
        split_hand: If the player split, the second Hand to play next.
    """
    def __init__(self, name):
        self.name = name
        # Hand will be assigned by Game.setup with the shared deck.
        self.hand = None
        self.points = 0
        self.turn_over = False
        self.doubled_down = False
        self.split_hand = None
        self.winning_state = None
        self.losing_state = None

    def reset_for_round(self):
        """Reset transient per-round state while keeping accumulated points and name."""
        if self.hand:
            self.hand.reset()
        self.turn_over = False
        self.doubled_down = False
        self.split_hand = None

class Dealer(Player):
    """Dealer (House) player. Points represent house points."""
    def __init__(self):
        super().__init__("Dealer")

class Hand:
    """A blackjack hand that manages card values and drawing from a deck.

    Notes:
    - If a shared Deck instance is provided, the Hand will draw from that deck.
    - If no Deck is provided, Hand creates and manages its own private deck.
    - Hand.cards stores labels (e.g., 'A♠') -> rank mapping for display and value calc.
    """
    def __init__(self, deck=None):
        self.all_cards = {
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5,
            '6': 6,
            '7': 7,
            '8': 8,
            '9': 9,
            '10': 10,
            'J': 10,
            'Q': 10,
            'K': 10,
            'A': 11
        }
        self.suits = ['♠', '♥', '♦', '♣']
        # cards maps label -> rank, e.g. {'A♠': 'A'}
        self.cards: dict[str, str] = {}
        # Deck management: use shared Deck if provided, otherwise maintain a private _deck
        self.deck = deck
        if self.deck is None:
            self.reset_deck()

    def reset_deck(self):
        """Create and shuffle a fresh 52-card private deck (rank, suit) list."""
        # deck is a list of (rank, suit)
        self._deck: list[tuple[str, str]] = [(r, s) for r in self.all_cards for s in self.suits]
        random.shuffle(self._deck)

    def draw_one_dealer(self):
        """Draw a single card for dealer's first visible card and show concealed second."""
        self.draw_one()
        print(f"\033[36mDealer's hand: {' '.join(self.cards.keys())} Hidden\033[0m")

    def draw_second_dealer(self):
        """Draw dealer's second card and reveal full hand and total."""
        self.draw_one()
        print(f"\033[36mDealer's hand: {' '.join(self.cards.keys())}\033[0m")
        print(f"\033[36mDealer's Total: {self.value()}\033[0m")
    
    def hit_dealer(self) -> str:
        """Dealer draws one card, prints picked card and current totals; returns label."""
        picked_label = self.draw_one()
        print(f"\n\033[36mPicked card: {picked_label}\033[0m\n")
        print(f"\033[36mDealer's hand: {' '.join(self.cards.keys())}\033[0m")
        print(f"\033[36mDealer's Total: {self.value()}\033[0m")
        return picked_label
    
    def stand_dealer(self):
        """Dealer stands — print final dealer hand and total."""
        print(f"\033[36mDealer stands: {' '.join(self.cards.keys())}  Total: {self.value()}\033[0m")

    def draw_one(self) -> str:
        """Draw a single card from the shared deck or private deck and add to hand.

        Returns:
            str: The label of the drawn card, e.g. 'A♠'.
        """
        if self.deck is not None:
            rank, suit = self.deck.draw()
        else:
            if not self._deck:
                self.reset_deck()
            rank, suit = self._deck.pop()
        label = f"{rank}{suit}"
        self.cards[label] = rank
        return label
    
    def draw(self, n=2):
        """Draw n cards into the hand and return a string of labels (for display)."""
        for _ in range(n):
            self.draw_one()
        return ' '.join(self.cards.keys())

    def value(self):
        """Return best total <= 21 by downgrading aces (11->1) as needed."""
        total, aces = 0, 0
        for label, rank in self.cards.items():
            total += self.all_cards[rank]
            if rank == 'A':
                aces += 1
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total
        
    def reset(self):
        """Clear current hand. Do not reset a shared deck; reset private deck only."""
        self.cards.clear()
        # Only reset private deck; shared deck is managed externally by Game.
        if self.deck is None:
            self.reset_deck()

    def can_split(self):
        """True if exactly two cards with equal ranks (pair)."""
        if len(self.cards) == 2:
            ranks = list(self.cards.values())
            return ranks[0] == ranks[1]
        return False

    def hit(self) -> str:
        """Player hit: draw one card, print animated picked card and totals."""
        picked_label = self.draw_one()
        
        for char in f"\n\033[1mPicked card: {picked_label}\033[0m":
            time.sleep(0.1)
            print(char, end='', flush=True)
        print("\n")
        print(f"Cards in hand: {' '.join(self.cards.keys())}\n")
        print(f"Total: {self.value()}")

    def stand(self):
        """Player stands: print final hand and total."""
        print(f"\nCards: {' '.join(self.cards.keys())}, stands with total {self.value()}")

    def double(self):
        """Double down: draw one card and show final totals."""
        picked_label = self.draw_one()
        print(f"\nDouble down. Drew: {picked_label}")
        print(f"Cards in hand: {' '.join(self.cards.keys())}")
        print(f"Final total after double: {self.value()}")

    def split(self):
        """Split the hand into two hands if holding a pair.

        Returns a new Hand sharing the same deck with one of the cards moved.
        """
        if len(self.cards) != 2:
            print("\n\033[31mSplit is only allowed with two cards.\n\033[0m")
            return None
        
        ranks = list(self.cards.values())
        if ranks[0] != ranks[1]:
            print("\n\033[31mSplit requires a pair of equal ranks.\n\033[0m")
            return None
        
        # Move one labeled card into a new Hand that shares the same deck
        label_to_move, rank_to_move = next(iter(self.cards.items()))
        del self.cards[label_to_move]
        new_hand = Hand(self.deck)

        new_hand.cards[label_to_move] = rank_to_move
        print(f"Cards: {' '.join(self.cards.keys())} splits into {' '.join(new_hand.cards.keys())}")
        return new_hand

# -----------------------------------------------------------------------------
# Game coordination
# -----------------------------------------------------------------------------
class Game:
    """Coordinates the Blackjack game rounds, turns, and scoring."""
    def __init__(self):
        self._players = []
        self.round_over = False
        self.current_round = 0
        self.total_rounds = 1

        # Shared deck ranks and suits (used to create the shared Deck)
        self._ranks = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
        self._suits = ['♠','♥','♦','♣']

        # Create shared deck (will be reset at each round start)
        self.deck = Deck(self._ranks, self._suits)

        self.setup()
        # Run configured number of rounds
        for r in range(1, self.total_rounds + 1):
            self.current_round = r
            print("\n" + "=" * 12 + f" Round {r}/{self.total_rounds} " + "=" * 12)
            self.game()
            # Prepare for next round
            if r < self.total_rounds:
                self.reset_round()
        # After all rounds, show final standings
        self.print_final_standings()

    @property
    def players(self):
        return self._players

    def setup(self):
        """Prompt for players and number of rounds; initialize dealer and assign shared deck."""
        while True:
            try:
                num_players = int(input("\nHow many players: "))
                break
            except ValueError:
                print("\033[31mInvalid input. Please enter a number.\033[0m")

        self._players = []
        print("\n")
        for i in range(num_players):
            self.name = input(f"- Name of player {i+1}? ")
            player = Player(self.name)
            # Assign a Hand that shares the central deck
            player.hand = Hand(self.deck)
            self._players.append(player)

        self.dealer = Dealer()
        # Assign dealer hand sharing the central deck
        self.dealer.hand = Hand(self.deck)

        while True:
            try:
                self.total_rounds = int(input("\nHow many rounds? "))
                if self.total_rounds <= 0:
                    raise ValueError()
                break
            except ValueError:
                print("\033[31mInvalid input. Please enter a positive number.\033[0m")

    def manage_split(self):
        # Insert the split hand as a new player right after the current player
        i = 0
        while i < len(self._players):
            player = self._players[i]
            if player.hand.can_split():
                new_hand = player.hand.split()
                if new_hand:
                    new_player = Player(f"{player.name} (2)")
                    new_player.hand = new_hand
                    self._players.insert(i + 1, new_player)
                    i += 1  # skip over the newly inserted player
            i += 1

    def reset_round(self):
        """Reset all hands and per-round flags while keeping cumulative points."""
        # Reset the shared deck for the new round
        self.deck.reset()
        for p in self._players:
            p.reset_for_round()
            # reassign fresh Hand instances sharing the same deck
            p.hand = Hand(self.deck)
        # Reset dealer hand/flags too
        if hasattr(self, 'dealer') and self.dealer:
            self.dealer.reset_for_round()
            self.dealer.hand = Hand(self.deck)
        # Clear game-level flags
        self.winning_state = None
        self.losing_state = None

    def dealer_first_turn(self):
        self.dealer.hand.draw_one_dealer()

    def dealer_second_turn(self):
        self.dealer.hand.draw_second_dealer()

    def dealer_turn(self):
        """Draw until dealer reaches 17 or more; show final stand if <= 21."""
        while self.dealer.hand.value() < 17:
            print("")
            time.sleep(1)
            for char in f"\033[1mDealer hits!\033[0m":
                print(char, end="", flush=True)
                time.sleep(0.1)
            self.dealer.hand.hit_dealer()
        if self.dealer.hand.value() <= 21:
            self.dealer.hand.stand_dealer()

    def game(self):
        """Play one complete round: deal, player turns, dealer turn, results, scoring."""
        self.winning_state = None
        self.losing_state = None
        print("\n" + "-" * 42)
        if getattr(self, 'current_round', 0) and getattr(self, 'total_rounds', 0):
            print(f"\033[34mStarting Round {self.current_round}/{self.total_rounds}\033[0m")

        # Ensure deck is fresh at the start of a round
        self.deck.reset()

        # Dealer shows first upcard
        self.dealer_first_turn()

        def try_shift_to_split(player):
            if player.split_hand is not None:
                player.hand = player.split_hand
                player.split_hand = None
                cards = ' '.join(player.hand.cards.keys())
                print(f"\n\033[33mNow playing split hand for {player.name}: {cards}\033[0m")
                return True
            return False

        for player in self._players:
            player.turn_over = False
            ha = player.hand.draw()
            print("-" * 42)
            print(f"\n\033[35m{player.name}'s Cards: {ha}\033[0m")

            while not player.turn_over:
                print(f"\n\033[1m{player.name}'s turn:\033[0m")
                if player.hand.value() == 21 and len(player.hand.cards) == 2:
                    time.sleep(1)
                    print(f"\n\033[32m{player.name} Hits a Royal Blackjack!\033[0m\n")
                    if try_shift_to_split(player):
                        continue
                    self.winning_state = "BLACKJACK"
                    time.sleep(1)
                    break
                action = input("(H)it , (S)tand , (D)ouble , or (Sp)lit? ").strip().upper()

                if action == "H":
                    player.hand.hit()
                    val = player.hand.value()
                    if val > 21:
                        for char in f"\n\033[31m{player.name} Busts with a total of {val}\033[0m\n":
                            print(char, end='', flush=True)
                            time.sleep(0.07)
                        print()
                        if try_shift_to_split(player):
                            continue
                        player.turn_over = True
                        self.losing_state = "BUST"

                    elif val == 21:
                        print(f"\n\033[32m{player.name} Hits Blackjack!\033[0m\n")
                        if try_shift_to_split(player):
                            continue
                        self.winning_state = "PLAYER_WIN"

                elif action == "S":
                    player.hand.stand()
                    if try_shift_to_split(player):
                        continue
                    player.turn_over = True
                    time.sleep(1)

                elif action == "D":
                    # Double down is allowed only on the first two cards and only once
                    if len(player.hand.cards) != 2 or player.doubled_down:
                        print("\033[31mDouble down is only allowed on your first two cards and only once.\033[0m")
                        continue
                    player.hand.double()
                    val = player.hand.value()
                    player.doubled_down = True
                    if val > 21:
                        for char in f"\033[31m{player.name} Busts with a total of {val}\033[0m":
                            print(char, end='', flush=True)
                            time.sleep(0.07)
                        print()
                        if try_shift_to_split(player):
                            continue
                        player.turn_over = True
                        self.losing_state = "DOUBLE_DOWN"
                    if val == 21:
                        print(f"\n\033[32m{player.name} Hits Blackjack With A Double Down!\033[0m\n")
                        if try_shift_to_split(player):
                            continue
                    if try_shift_to_split(player):
                        continue
                    self.winning_state = "DOUBLE_DOWN"
                    player.turn_over = True

                elif action == "SP":
                    if player.hand.can_split():
                        new_hand = player.hand.split()
                        if new_hand:
                            player.split_hand = new_hand
                            print("\n\033[33mSplit created. (Finish this hand, then you'll play the split hand.)\033[0m")
                    else:
                        print("\033[31mCannot split: not a pair or not exactly two cards.\033[0m")

                else:
                    print("\033[31mInvalid choice. Try again.\033[0m")
                    # loop continues for new input

        print("\n" + "-" * 42)
        self.dealer_second_turn()
        self.dealer_turn()
        print("\n" + "-" * 42)
        time.sleep(2)
        self.get_winner()
        time.sleep(2)
        self.cal_points()
        input("\nPress Enter to continue to the next round...")
        time.sleep(1)
        print("\n\n")
        time.sleep(0.5)

    def get_winner(self):
        """Print outcome messages comparing each player against the dealer total."""
        dealer_value = self.dealer.hand.value()

        if dealer_value > 21:
            # Dealer busts: any player <= 21 wins
            print(f"\n\033[36mDealer Busts with a total of {dealer_value}\033[0m\n")
            print("\033[92mPlayers who did not bust win!\033[0m\n")
            for player in self._players:
                pv = player.hand.value()
                if pv <= 21:
                    print(f"\033[32m{player.name} Won with a total of {pv}\033[0m")
                else:
                    print(f"\033[31m{player.name} Lost with a total of {pv}\033[0m")

        elif dealer_value == 21:
            # Dealer blackjack: only players with 21 push; others lose
            print(f"\n\033[32mDealer Hits Blackjack!\033[0m\n")
            for player in self._players:
                pv = player.hand.value()
                if pv == 21:
                    print(f"\033[33m{player.name} Ties with the Dealer at 21!\033[0m")
                else:
                    print(f"\033[91m{player.name} Loses with a total of {pv}\033[0m")

        else:
            # Compare each player to dealer; busts lose
            for player in self._players:
                pv = player.hand.value()
                if pv > 21:
                    print(f"\033[91m{player.name} Loses with a total of {pv}\033[0m")
                elif pv > dealer_value:
                    print(f"\033[32m{player.name} Wins with a total of {pv}\033[0m")
                elif pv == dealer_value:
                    print(f"\033[33m{player.name} Ties with the Dealer at {pv}\033[0m")
                else:
                    print(f"\033[91m{player.name} Loses with a total of {pv}\033[0m")
                    

    def points(self, player: Player, dealer_value: int) -> int:
        """Compute points earned by a single player for this round.

        Returns:
            int: Points per rules (wins 1, double/natural 2, push 0, double-loss -1, normal loss 0)
        """
        
        """
        Rules (simple):
        - Bust or loss -> 0
        - Push -> 0
        - Win -> 1
        - Win with Double Down -> 2
        - Natural Blackjack -> 2
        """
        pv = player.hand.value()
        # Busts: lose 1 if doubled, else 0
        if pv > 21:
            return -1 if player.doubled_down else 0

        # Natural blackjack (2-card 21)
        is_natural_blackjack = (pv == 21 and len(player.hand.cards) == 2)

        # Dealer busts -> any non-busted player wins
        if dealer_value > 21:
            return 2 if player.doubled_down or is_natural_blackjack else 1

        # Non-bust dealer: compare totals
        if pv > dealer_value:
            return 2 if player.doubled_down or is_natural_blackjack else 1
        if pv == dealer_value:
            return 0  # push
        # Loss
        return -1 if player.doubled_down else 0
            
    def cal_points(self):
        """Accrue points for players and the House (dealer) and print a summary."""
        dealer_value = self.dealer.hand.value()
        print("\n" + "-" * 42)
        print(f"\033[36mDealer final total: {dealer_value}\033[0m")

        if dealer_value > 21:
            print("\033[36mDealer busts. Eligible player wins are counted.\033[0m")
        elif dealer_value == 21:
            print("\033[36mDealer has 21. Players must tie at 21 to push.\033[0m")

        # Score each player and accumulate to their running total
        house_round_points = 0
        for player in self._players:
            earned = self.points(player, dealer_value)
            player.points += earned
            pv = player.hand.value()
            is_push = (pv == dealer_value and pv <= 21 and dealer_value <= 21)
            # Determine outcome against house
            dealer_bust = dealer_value > 21
            player_wins = (dealer_bust and pv <= 21) or (dealer_value <= 21 and pv <= 21 and pv > dealer_value)
            player_loses = (pv > 21) or (dealer_value <= 21 and pv < dealer_value)
            # House points: +1 per player loss; -1 per normal win; -2 per double-down win
            if player_wins:
                house_round_points -= (2 if player.doubled_down else 1)
            elif player_loses:
                house_round_points += 1
            status = (
                "wins with double x2" if earned == 2 else
                "wins" if earned == 1 else
                "push" if is_push else
                "loses"
            )
            color = "\033[32m" if earned > 0 else ("\033[33m" if is_push else "\033[31m")
            sign = "+" if earned > 0 else ""
            print(f"{color}{player.name} {status} -> {sign}{earned} point(s). Total: {player.points}\033[0m")

        # Add to dealer (House) cumulative points
        self.dealer.points += house_round_points
        house_delta_word = "gains" if house_round_points >= 0 else "loses"
        print(f"\n\033[34mHouse {house_delta_word} {abs(house_round_points)} point(s) this round. \nTotal House points: {self.dealer.points}\033[0m")

    def print_final_standings(self):
        """Print a final ranking of players and the House by total points."""
        print("\n" + "#" * 12 + " Final Standings " + "#" * 12)
        standings = [(p.name, p.points) for p in self._players]
        standings.append(("House", self.dealer.points))
        standings.sort(key=lambda x: x[1], reverse=True)
        print('\n')
        for idx, (name, pts) in enumerate(standings, start=1):
            print(f"{idx}. {name}: {pts} point(s)")
        # Highlight top rank (including ties)
        if standings:
            top_score = standings[0][1]
            leaders = [name for name, pts in standings if pts == top_score]
            if len(leaders) == 1:
                print(f"\n\033[1mTop rank: {leaders[0]} with {top_score} point(s)\033[0m")
            else:
                leaders_list = ", ".join(leaders)
                print(f"\n\033[1mTop rank tie: {leaders_list} with {top_score} point(s)\033[0m")

def main():
    print("\033[1mWelcome to Blackjack!\033[0m")
    game = Game()

    # After each round
    game.reset_round()

if __name__ == "__main__":
    main()
