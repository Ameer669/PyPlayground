import time  # time delay
import random  # random number generation
import json  # JSON file handling
import sys  # text delay
from rich.console import Console  # rich console for styled output
from rich.table import Table  # rich table for inventory display
from rich.panel import Panel  # rich panel for enhanced UI
from rich.text import Text  # rich text for styled output
import pygame.mixer  # sound handling
from colorama import Fore, Style  # Add colorama for colored text
from prompt_toolkit.validation import Validator, ValidationError 
# prompt_toolkit for input validation
from asciimatics.screen import Screen # Import Screen for handling screen operations
from asciimatics.scene import Scene # Import Scene for managing scenes
from asciimatics.effects import Cycle, Stars, Print, Matrix  # Import necessary effects
from asciimatics.renderers import FigletText, Rainbow  # Import FigletText and Rainbow for text effects
import threading # threading for concurrent operations


class ChoiceValidator(Validator):
    def __init__(self, valid_choices):
        self.valid_choices = valid_choices

    def validate(self, document):
        try:
            choice = int(document.text.strip())
            if choice not in self.valid_choices:
                raise ValidationError(
                    message=f"Please select a valid option from {', '.join(map(str, self.valid_choices))}.",
                    cursor_position=len(document.text)
                )
        except ValueError:
            raise ValidationError(
                message="Please enter an integer.",
                cursor_position=len(document.text)
            )


class GameIntro:
    def __init__(self):
        self.min_height = 10
        self.min_width = 40
        self.stop_intro = False

    def intro(self, screen):
        def title_screen(screen):
            effects = [
                Cycle(screen, FigletText("My", font='big'), screen.height // 2),
                Cycle(screen, FigletText("Adventure", font='big'), screen.height // 2 - 5),
                Cycle(screen, FigletText("Game", font='big'), screen.height // 2),
                Stars(screen, 200)
            ]
            return Scene(effects, 60)

        def matrix_effect_screen(screen):
            effects = [
                Matrix(screen, stop_frame=100),
                Print(screen, FigletText("Prepare Yourself!", font='slant'), screen.height // 2, speed=1, start_frame=20),
            ]
            return Scene(effects, 60)

        def forest_effect_screen(screen):
            effects = [
                Print(screen, Rainbow(screen, FigletText("Into the Unknown", font='big')), screen.height // 2, speed=1),
                Stars(screen, 100)
            ]
            return Scene(effects, 60)

        while screen.height < self.min_height or screen.width < self.min_width:
            print(f"Error: Terminal size too small. Required: {self.min_width}x{self.min_height}.")
            input("Resize and press Enter: ")
            screen.clear()

        scenes = [
            title_screen(screen),
            matrix_effect_screen(screen),
            forest_effect_screen(screen)
        ]
        scenes = [scene for scene in scenes if scene.effects]
        if not scenes:
            print("Error: No valid scenes available to play. Please resize your terminal.")
            return

        try:
            scenes = [title_screen(screen)]  
            screen.play(scenes, stop_on_resize=False, repeat=False)

        finally:
            screen.close()

    def play_intro(self):
        try:
            Screen.wrapper(self.intro)
        except Exception as e:
            print(f"Error running intro screen: {e}")
        finally:
            import sys
            # Reset the terminal state thoroughly
            print("\033[0m", end="")      # Reset colors
            print("\033[?25h", end="")    # Show cursor
            print("\033[?1049l", end="")  # Exit alternate buffer (if used by asciimatics)
            print("\033[2J", end="")      # Clear screen
            print("\033[H", end="")         # Move cursor to home position
            print("\033[?1049h", end="")  # Enter an alternate buffer (if used by asciimatics)
            print("\033[?1l", end="")     # Disable line wrap
            sys.stdout.flush()            # Force output
            # Additional reset for Windows terminals
            print("", flush=True)


class AdventureGame:
    def __init__(self, story_file, items_file = "items.json"):
        with open(story_file, 'r') as f:
            self.story = json.load(f)
        with open(items_file, 'r') as f:
            self.items = json.load(f)
        
        self.all_items = {}
        for category, items in self.items["items"].items():
            if isinstance(items, dict):
                self.all_items.update(items)
            else:
                print(f"Warning: Category '{category}' is not a dictionary of items.")
                
        try:
            self.find_item_sound = pygame.mixer.Sound("fast-sword-whoosh.wav")
            self.craft_sound = pygame.mixer.Sound("craft_success.wav")
            self.item_break_sound = pygame.mixer.Sound("item_break.wav")
        except pygame.error as e:
            print(f"Warning: Could not load sound files: {e}")
            self.find_item_sound = None
            self.craft_sound = None
            self.item_break_sound = None

        self.current = "start"
        self.hp = self.story.get("player", {}).get("hp", 100)
        self.base_attack_power = random.randint(12, 20)
        self.base_defense_power = 5
        self.equipped_items = []
        self.inventory = []
        self.items = {}
        self.player_status = {}
        self.time_of_day = "day"
        self.console = Console()

    def type_text(self, text, delay=0.05, rich_style=""):
        for char in text:
            print(Text(char, style=rich_style), end="", flush=True)
            time.sleep(delay)
        self.console.print()  

    def play_sound(self, sound_object):
        
        if sound_object:
            try:
                sound_object.play()
            except pygame.error as e:
                self.console.print(f"Error playing sound: {e}", style="red")
        
        
            
    def cleanup(self):
        pygame.mixer.quit()
        time.sleep(0.05)
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def get_attack_power(self):
        bonus = sum(item.get("attack_bonus", 0) for item in self.equipped_items)
        return self.base_attack_power + bonus

    def get_defense_bonus(self):
        bonus = sum(item.get("defense_bonus", 0) for item in self.equipped_items)
        return self.base_defense_power + bonus

    def toggle_time_of_day(self, node):
        """Set the time of day based on the current node's specification."""
        if node.get("make_night", False):
            self.cleanup()
            self.time_of_day = "night"        
            self.type_text(Fore.LIGHTMAGENTA_EX + "\nStars twinkle above as darkness falls." + Style.RESET_ALL, delay=0.05)
            time.sleep(0.5)
            self.type_text(Fore.LIGHTMAGENTA_EX + "\nIt is now night." + Style.RESET_ALL, delay=0.05)
            self.cleanup()
        elif node.get("make_day", False):
            self.cleanup()
            self.time_of_day = "day"
            self.type_text(Fore.LIGHTMAGENTA_EX + "\nSunlight spills over the horizon." + Style.RESET_ALL, delay=0.05)
            time.sleep(0.5)
            self.type_text(Fore.LIGHTMAGENTA_EX + "\nIt is now day." + Style.RESET_ALL, delay=0.05)
            self.cleanup()
    
    def change_weather(self, node):
        """Randomly change the weather."""
        self.weather = "clear"
        self.weather_types = ["clear", "rainy", "foggy", "stormy"]
        self.weather_effects = {
            "clear": {
                "miss_chance_modifier": 0,
                "description": "Bright skies shine above, not a cloud in sight."
            },
            "rainy": {
                "miss_chance_modifier": 0.10,
                "description": "Gentle rain falls, leaving the ground slick."
            },
            "foggy": {
                "miss_chance_modifier": 0.20,
                "description": "Thick fog swirls, cloaking the path ahead."
            },
            "stormy": {
                "miss_chance_modifier": 0.30,
                "description": "A fierce storm rages, lightning splitting the sky."
            },
            "windy": {
                "miss_chance_modifier": 0.15,
                "description": "A brisk wind howls through the trees, stirring dust and leaves."
            },
            "misty": {
                "miss_chance_modifier": 0.25,
                "description": "A ghostly mist drifts around you, softening every sound."
            },
            "scorching": {
                "miss_chance_modifier": 0.20,
                "description": "Blazing sun beats down, heat shimmering off the ground."
}
        }
        if node.get("weather", False):
            self.cleanup()
            weather = node.get("weather", "clear")
            self.weather = weather
            self.cleanup()
            time.sleep(0.5)
            self.type_text(Fore.MAGENTA + f"\n\n\n\n\nThe weather changes...\n" + Style.RESET_ALL, delay=0.07)
            time.sleep(0.5)
            self.type_text(Fore.MAGENTA + f"\n{self.weather_effects[self.weather]['description']}" + Style.RESET_ALL, delay=0.07)
            time.sleep(0.5)
                
    def get_validated_input(self, prompt_text, valid_choices):
        """Get validated input from the user with error handling."""
        while True:
            try:
                # Display the prompt
                self.console.print(prompt_text, end="", style="yellow")
                # Get raw input without using PromptSession
                raw_input = input().strip()
                
                # Try to convert to integer
                choice = int(raw_input)
                
                # Check if the choice is valid
                if choice in valid_choices:
                    return choice
                else:
                    self.console.print(f"\nPlease select a valid option from {', '.join(map(str, valid_choices))}.\n", style="red")
                    time.sleep(0.5)
            except ValueError:
                # Handle non-integer input
                self.console.print("\nPlease enter a valid number.\n", style="red")
                time.sleep(0.5)
            except KeyboardInterrupt:
                # Handle Ctrl+C
                self.console.print("\nGame interrupted. Exiting...\n", style="red")
                self.current = "end"
                self.cleanup()
                sys.exit(0)
                
    def combat(self, enemy_key):
        enemy = self.story["enemies"][enemy_key]
        enemy_attack_range = enemy["attack_range"]
        enemy_hp = enemy["hp"]
        enemy_defense = enemy.get("defense", 0)
        miss_chance = 0.3 if self.time_of_day == "night" else 0.1
        
        while enemy_hp > 0 and self.hp > 0:
            self.console.print(Panel(f"Combat: You are fighting {enemy['name']}!", style="bold red", border_style="red"))
            time.sleep(0.5)
            # Display combat stats in a table
            stats_table = Table()
            stats_table.add_column("You", style="blue")
            stats_table.add_column("Enemy", style="red")
            self.min_attack_power = 12 + sum(item.get("attack_bonus", 0) for item in self.equipped_items)
            self.max_attack_power = 20 + sum(item.get("attack_bonus", 0) for item in self.equipped_items)
            stats_table.add_row(f"HP: {self.hp}", f"HP: {enemy_hp}")
            stats_table.add_row(f"Attack: {self.min_attack_power}-{self.max_attack_power}", f"Attack: {enemy_attack_range[0]}-{enemy_attack_range[1]}")
            stats_table.add_row(f"Defense: {self.get_defense_bonus()}", f"Defense: {enemy_defense}")
            self.console.print(stats_table)
            self.console.print(f"Miss Chance: {miss_chance * 100:.0f}%", style="yellow")
            time.sleep(0.5)
            self.console.print("Options:", style="yellow")
            self.console.print("1. Attack", style="yellow")
            self.console.print("2. Use Item", style="yellow")
            self.console.print("3. Flee", style="yellow")
            choice = self.get_validated_input("Your choice: ", [1, 2, 3])
            self.console.rule(style="white")

            if choice == 1:
                if random.random() < miss_chance:
                    time.sleep(1)
                    self.type_text("You missed your attack!", delay=0.03, rich_style="red")
                else:
                    attack_power = random.randint(self.min_attack_power, self.max_attack_power)
                    damage_to_enemy = max(0, attack_power - enemy_defense)
                    enemy_hp -= damage_to_enemy
                    time.sleep(1)
                    self.type_text(Fore.LIGHTGREEN_EX + f"You deal {damage_to_enemy} damage to the enemy." + Style.RESET_ALL, delay=0.03, rich_style="green")
                    
                    if enemy_hp <= 0:
                        time.sleep(1)
                        self.type_text(Fore.LIGHTGREEN_EX + f"You defeated {enemy['name']}!" + Style.RESET_ALL, delay=0.03, rich_style="green")
                        return "win"
                enemy_attack = random.randint(*enemy_attack_range)
                defense = self.get_defense_bonus()
                damage_to_player = max(0, enemy_attack - defense)
                self.hp -= damage_to_player
                self.type_text(Fore.RED+ f"The enemy deals {damage_to_player} damage to you."+ Style.RESET_ALL, delay=0.03)
                if self.hp <= 0:
                    time.sleep(1)
                    self.type_text(Fore.RED + "\nYou were defeated by the enemy.\n"+ Style.RESET_ALL, delay=0.07)
                    time.sleep(1)
                    return "lose"
            elif choice == 2: 
                self.open_inventory(in_combat=True)
                if self.hp <= 0: return "lose"
                if enemy_hp <=0: return "win"
            elif choice == 3:
                flee_success_chance = 0.5
                if any(item.get("name") == "Shadow Cloak" and item.get("special_ability") == "stealth" for item in self.equipped_items):
                    flee_success_chance = 0.75
                    
                if random.random() < flee_success_chance:
                    time.sleep(1)
                    self.type_text(Fore.RED + f"You failed to flee from {enemy['name']}!"+ Style.RESET_ALL, delay=0.05, rich_style="yellow")
                    damage = random.randint(*enemy_attack_range)
                    self.hp -= damage
                    self.type_text(Fore.RED+ f"The enemy deals {damage} damage to you."+ Style.RESET_ALL, delay=0.04)
                    time.sleep(0.5)
                else:
                    time.sleep(1)
                    self.type_text(Fore.BLUE + f"\nYou fled from {enemy['name']}."+ Style.RESET_ALL, delay=0.05)
                    time.sleep(1)
                    return "flee" 
        if enemy_hp <= 0:
            return "win"

    def open_inventory(self, in_combat=False):
        if not self.inventory:
            self.console.print("You have no items in your inventory!", style="yellow")
            return
        while True:
            time.sleep(0.5)
            self.console.print("")
            table = Table(title="Inventory", border_style="cyan", style="green")
            table.add_column("#", style="cyan")
            table.add_column("Name", style="magenta")
            table.add_column("Type", style="green")
            table.add_column("Info", style="yellow")  
            
            for i, item in enumerate(self.inventory, 1):
                name = item['name']
                item_type = item['type']
                info_str = "N/A"
                if "attack_bonus" in item: info_str = f"ATK +{item['attack_bonus']}"
                elif "defense_bonus" in item: info_str = f"DEF +{item['defense_bonus']}"
                elif "hp_restore" in item: info_str = f"HP +{item['hp_restore']}"
                elif "effect" in item: info_str = f"Effect {item['effect']}"
                elif "special_ability" in item: info_str = f"Ability {item['special_ability']}"
                elif "light_radius" in item: info_str = f"Light {item['light_radius']}"
                table.add_row(str(i), name, item_type, str(info_str))

            self.console.print(table)
            time.sleep(0.5)
            self.console.print(f"\n{len(self.inventory) + 1}. Exit Inventory", style="cyan")

            try:
                choice = self.get_validated_input("Choose an item (number): ",
                                                  list(range(1, len(self.inventory) + 2))) - 1
                if 0 <= choice < len(self.inventory):
                    selected_item = self.inventory[choice]
                    if selected_item["type"] == "consumable":
                        consumed = False
                        
                        
                        if selected_item.get("effect") == "cure_poison":
                            if "poisoned" in self.player_status and self.player_status["poisoned"]["active"]:
                                self.player_status["poisoned"]["active"] = False
                                self.type_text(f"You used {selected_item['name']} and cured your poison!", rich_style="bold green")
                                consumed = True
                            else:
                                self.type_text("You are not poisoned.", rich_style="yellow")
                        elif "hp_restore" in selected_item:
                            self.hp = min(100, self.hp + selected_item.get("hp_restore", 0))
                            self.type_text(f"You used {selected_item['name']} and restored {selected_item.get('hp_restore', 0)} HP. Current HP: {self.hp}", rich_style="green")
                            consumed = True
                        elif selected_item.get("effect") == "strength_boost":
                            self.player_status["strength_boost"] = {
                                "active": True, 
                                "duration": selected_item.get("duration", 3),
                                "bonus": selected_item.get("attack_boost_amount", 5)
                            }
                            self.type_text(f"You used {selected_item['name']}. You feel a temporary surge of strength!", rich_style="yellow")
                            consumed = True
                        
                        if consumed:
                            self.inventory.pop(choice)
                        if in_combat and consumed: return

                    elif selected_item["type"] == "equipable":
                        if selected_item in self.equipped_items:
                            self.equipped_items.remove(selected_item)
                            # self.inventory.append(selected_item) # Item is already in inventory if unequipped, this would duplicate
                            self.type_text(f"You unequipped {selected_item['name']}.", style="yellow")
                        else:
                            can_equip = True
                            item_slot = None
                            if "attack_bonus" in selected_item: item_slot = "weapon"
                            elif "defense_bonus" in selected_item: item_slot = "armor"
                            elif selected_item.get("special_ability") == "stealth": item_slot = "cloak"

                            if item_slot:
                                for eq_item in self.equipped_items[:]: # Iterate copy for safe removal
                                    eq_item_slot = None
                                    if "attack_bonus" in eq_item: eq_item_slot = "weapon"
                                    elif "defense_bonus" in eq_item: eq_item_slot = "armor"
                                    elif eq_item.get("special_ability") == "stealth": eq_item_slot = "cloak"
                                    if eq_item_slot == item_slot:
                                        self.type_text(f"You already have an item in the {item_slot} slot ({eq_item['name']}). Unequipping it.", style="red")
                                        self.equipped_items.remove(eq_item) # Unequip old item
                                        self.inventory.append(eq_item) # Add old item back to general inventory
                                        break 
                            
                            if can_equip:
                                self.equipped_items.append(selected_item)
                                self.inventory.pop(choice)
                                self.type_text(Fore.LIGHTYELLOW_EX + f"You equipped {selected_item['name']}." + Style.RESET_ALL, delay = 0.03)
                    else:
                        self.type_text(f"{selected_item['name']} is a {selected_item['type']} item. {selected_item.get('description', '')}", style="cyan")
                elif choice == len(self.inventory):
                    self.type_text(Fore.LIGHTYELLOW_EX +"\nExiting inventory...\n"+ Style.RESET_ALL, delay=0.03)
                    break
            except ValidationError:
                pass 
    
    def apply_status_effects(self):
        if "poisoned" in self.player_status and self.player_status["poisoned"]["active"]:
            status = self.player_status["poisoned"]
            damage = status.get("damage_per_turn", 5)
            self.hp -= damage
            self.type_text(f"You take {damage} damage from poison.", rich_style="bold red")
            status["duration"] -= 1
            if status["duration"] <= 0:
                self.type_text("The poison has worn off.", rich_style="bold green")
                status["active"] = False
            if self.hp <= 0:
                self.type_text("You succumbed to the poison!", rich_style="bold red")
                self.current = "end"
        if "strength_boost" in self.player_status and self.player_status["strength_boost"]["active"]:
            status = self.player_status["strength_boost"]
            status["duration"] -=1
            if status["duration"] <= 0:
                self.type_text("Your strength boost has worn off.", rich_style="bold yellow")
                status["active"] = False
                # No need to pop, just set to inactive. get_attack_power will ignore inactive boosts.
    
    def body(self):
        if not self.equipped_items:
            self.console.print("\nYou have no equipped items!\n", style="yellow")
        else:
            self.console.print("\nEquipped Items:", style="bold magenta")
            for i, item in enumerate(self.equipped_items, 1):
                self.console.print(f"{i}. {item['name']} ({item['type']})", style="cyan")

        self.console.print(f"{len(self.equipped_items) + 1}. Exit", style="cyan")

        try:
            choice = self.get_validated_input("Choose an option (number): ",
                                              list(range(1, len(self.equipped_items) + 2))) - 1
            if 0 <= choice < len(self.equipped_items):
                selected_item = self.equipped_items.pop(choice)
                self.inventory.append(selected_item)
                self.console.print(f"You unequipped {selected_item['name']}.", style="yellow")
            elif choice == len(self.equipped_items):
                time.sleep(1)
                self.type_text(Fore.LIGHTYELLOW_EX + "\nExiting body menu..." + Style.RESET_ALL, delay=0.03)
                time.sleep(1)
        except ValidationError:
            pass

    def manage_equipable_items(self):
        equipable_items = [item for item in self.inventory if item["type"] == "equipable"]
        if not equipable_items:
            self.console.print("You have no equipable items in your inventory!", style="yellow")
            return

        self.console.print("\nEquipable Items:", style="bold magenta")
        for i, item in enumerate(equipable_items, 1):
            bonus_type = "Defense Bonus" if "defense_bonus" in item else "Attack Bonus"
            bonus_value = item.get("defense_bonus", item.get("attack_bonus", 0))
            self.console.print(f"{i}. {item['name']} ({bonus_type}: {bonus_value})", style="cyan")
        self.console.print(f"{len(equipable_items) + 1}. Don't equip/unequip any item", style="cyan")

        try:
            choice = int(input("Choose an item to equip/unequip (number): ")) - 1

            if 0 <= choice < len(equipable_items):
                selected_item = equipable_items[choice]
                if selected_item in self.equipped_items:
                    self.equipped_items.remove(selected_item)
                    self.inventory.append(selected_item)
                    self.console.print(f"\nYou unequipped {selected_item['name']}.\n", style="yellow")

                else:
                    if "attack_bonus" in selected_item:
                        # Ensure only one attack item is equipped
                        for item in self.equipped_items:
                            if "attack_bonus" in item:
                                self.console.print("You can only equip one attack item at a time!", style="red")
                                return
                    elif "defense_bonus" in selected_item:
                        # Ensure only one defense item is equipped
                        for item in self.equipped_items:
                            if "defense_bonus" in item:
                                self.console.print("You can only equip one defense item at a time!", style="red")
                                return
                    self.equipped_items.append(selected_item)
                    self.inventory.remove(selected_item)
                    self.console.print(f"\nYou equipped {selected_item['name']}.\n", style="yellow")
            elif choice == len(equipable_items):
                self.console.print("You chose not to equip/unequip any item.", style="cyan")
            else:
                time.sleep(0.5)
                self.type_text(Fore.RED + "\nInvalid choice!" + Style.RESET_ALL)
                time.sleep(0.5)
        except ValueError:
            self.console.print("Please enter a valid number!", style="red")

    def handle_choice(self, choice_data):
        """Handle the player's choice and check conditions."""
        if "condition" in choice_data:
            required_items = choice_data["condition"]
            if not all(req_item in [item["name"] for item in self.inventory] for req_item in required_items):
                self.console.print("You don't have the required items!", style="red")
                return

                # Remove the required items from the inventory
            for req_item in required_items:
                for item in self.inventory[:]:
                    if item["name"] == req_item:
                        self.inventory.remove(item)
                        break
            time.sleep(0.5)
            self.type_text(Fore.LIGHTYELLOW_EX + f"\nYou used: {', '.join(required_items)} to proceed!" + Style.RESET_ALL, delay=0.03)
            time.sleep(0.5)

            # Update the current node and HP
        self.current = choice_data["node"]
        self.hp = min(100, self.hp + choice_data.get("hp_change", 0))
        if self.hp <= 0:
            time.sleep(1)
            self.console.print(Panel("\nYou died! Game Over.", style="bold red", border_style="red"))
            self.current = "end"
        
    def sleep(self):
        """Handle the sleeping action."""
        self.type_text(Fore.MAGENTA + "\nYou decide to sleep..." + Style.RESET_ALL, delay=0.03)
        time.sleep(2)
        if self.time_of_day == "night":
            if random.random() < 0.4:
                self.type_text(Fore.LIGHTRED_EX + "\nYou are attacked by a wild animal while sleeping!" + Style.RESET_ALL, delay=0.03)
                wild_animal = self.story["enemies"]["wild_animal"]
                outcome = self.combat(wild_animal)
                if outcome != "win":
                    self.type_text("You failed to survive the wild animal attack.", delay=0.03, rich_style="red")
                    self.current = "end"
                    return
                # After combat, make it a day
                self.type_text("\nYou survived the attack and it is now a morning.", delay=0.03, rich_style="bold magenta")
                self.time_of_day = "day"
                return
        self.type_text(Fore.LIGHTGREEN_EX + "\nYou had a peaceful sleep and feel refreshed." + Style.RESET_ALL, delay=0.03)
        self.hp = min(100, self.hp + random.randint(10, 25))  # Restore some HP after sleeping
        time.sleep(0.5)
        self.type_text(Fore.LIGHTGREEN_EX +f"Your HP is now {self.hp}." + Style.RESET_ALL, delay=0.03)
        self.time_of_day = "day"
        self.type_text(Fore.MAGENTA +"\nIt is now day." + Style.RESET_ALL, delay=0.03)
        if "strength_boost" in self.player_status: self.player_status.pop("strength_boost")
        time.sleep(1)
    
    def display_node_info(self, node, show_inventory=True):
        self.cleanup()
        panel_style = "bold cyan"
        text_to_display = node['text']
        is_dark_area_node = "dark_area_description" in node
        has_light_source = False
        
        for item in self.inventory + self.equipped_items:
            if item.get("special_ability") in ["light_source_small", "light_source_medium", "light_source_strong"]:
                has_light_source = True
                break
            
        if is_dark_area_node and not has_light_source:
            text_to_display = node["dark_area_description"]
            panel_style = "dim white on black" # Style for dark areas
            
        self.console.rule(style="white")
        time.sleep(0.5)
        self.console.print(Panel(text_to_display, title=node.get("node_title", "Location"), style=panel_style, border_style="blue"))
        
        time.sleep(3)
        time.sleep(0.5)
        
        if "strength_boost" in self.player_status and self.player_status["strength_boost"]["active"]:
            self.type_text(f"(Strength Boost Active: {self.player_status['strength_boost']['duration']} turns left)", rich_style="yellow")
        if "poisoned" in self.player_status and self.player_status["poisoned"]["active"]:
            self.type_text(f"(Poisoned: {self.player_status['poisoned']['duration']} turns left)", rich_style="red")

    def play_game(self):
        found_items = set()  # Track items already found
        slept = False
        while self.current != "end":
            node = self.story[self.current]

            self.change_weather(node)
            
            if not slept:
                self.toggle_time_of_day(node)
            slept = False

                # Display node information (story text) before sleeping prompt
            if not hasattr(self, "inventory_opened") or not self.inventory_opened:
                self.display_node_info(node, show_inventory=False)
            self.inventory_opened = False

            if self.time_of_day == "night" and "sleep_choices" in node:
                self.type_text(Fore.LIGHTYELLOW_EX + "\nIt is night. You can choose to sleep or keep moving." + Style.RESET_ALL, delay=0.03)
                self.type_text(Fore.LIGHTYELLOW_EX + "1. Sleep" + Style.RESET_ALL, delay=0.03)
                self.type_text(Fore.LIGHTYELLOW_EX + "2. Keep moving" + Style.RESET_ALL, delay=0.03)
                try:
                    sleep_choice = int(input(Fore.LIGHTYELLOW_EX + "Your choice: " + Style.RESET_ALL).strip())
                    if sleep_choice == 1:
                        self.sleep()
                        slept = True
                        self.current = node["sleep_choices"]["sleep_node"]  
                        continue
                    elif sleep_choice == 2:
                        self.current = node["sleep_choices"]["move_node"]  
                        continue
                    else:
                        time.sleep(0.5)
                        self.type_text(Fore.RED + "\nInvalid choice! Please choose 1 or 2." + Style.RESET_ALL)
                        time.sleep(0.5)
                        continue
                except ValueError:
                    self.type_text("Invalid input! Please enter a number.", delay=0.03, rich_style="red")
                    continue
                
            if "items" in node:
                for item_name in node["items"]:
                    if item_name not in found_items:
                        try:
                            item = self.all_items[item_name]
                            self.inventory.append(item)
                            found_items.add(item_name)
                            self.type_text(Fore.LIGHTGREEN_EX + f"You found: {item['name']}" + Style.RESET_ALL, delay=0.03)
                            self.play_sound(self.find_item_sound)
                        except KeyError:
                            print(f"Warning: Item '{item_name}' not found in item database.")
                            
                            time.sleep(1)
                            
                        except KeyError:
                            print(f"Warning: Item '{item_name}' not found in item database.")

                # Display choices
            choices = list(node["choices"].keys())
            if not choices:
                self.current = "end"
                continue
            self.console.rule(style="white")
            self.type_text(f"Your HP: {self.hp}", delay=0.03, rich_style="green")

            self.min_attack_power = 12 + sum(item.get("attack_bonus", 0) for item in self.equipped_items)
            self.max_attack_power = 20 + sum(item.get("attack_bonus", 0) for item in self.equipped_items)
            self.type_text(f"Attack Power: ({self.min_attack_power}-{self.max_attack_power})", delay=0.03, rich_style="blue")

            defense_bonus = self.get_defense_bonus() - self.base_defense_power
            self.type_text(f"Defense: {self.base_defense_power}", delay=0.03, rich_style="blue")
            time.sleep(0.5)
            
            self.type_text(Fore.LIGHTBLUE_EX + "\nChoices:" + Style.RESET_ALL, delay=0.03, rich_style="bold yellow")
            
            for i, choice in enumerate(choices, 1):
                self.type_text(f"{i}. {choice}", delay=0.03, rich_style="cyan")
            time.sleep(0.2)
            self.type_text(f"{len(choices) + 1}. Open Inventory", delay=0.03, rich_style="yellow")
            self.type_text(f"{len(choices) + 2}. See Body", delay=0.03, rich_style="yellow")
            time.sleep(0.2)
            self.console.print("\nSelect an option by entering the number.", style="white")

            choice_num = self.get_validated_input("Your choice: ",
                                    list(range(1, len(choices) + 3))) - 1
            if 0 <= choice_num < len(choices):
                choice_text = choices[choice_num]
                choice_data = node["choices"][choice_text]
                
                if choice_data["type"] == "combat":
                    enemy = choice_data["enemy"]
                    outcome = self.combat(enemy)
                    if outcome == "win":
                        self.current = choice_data["win_node"]
                    elif outcome == "flee":
                        self.current = choice_data["flee_node"]
                else:
                    self.handle_choice(choice_data)
                    
            elif choice_num == len(choices):
                time.sleep(1)
                self.inventory_opened = True
                self.open_inventory()
            elif choice_num == len(choices) + 1:
                time.sleep(1)
                self.body()

            if self.hp <= 0:
                self.type_text("You died! Game Over.", delay=0.03, rich_style="red")
                self.current = "end"
            time.sleep(1)
        self.cleanup()
        self.console.rule(style="white")
        self.type_text(self.story["end"]["text"], delay=0.03, rich_style="bold cyan")
        self.type_text("\nThank you for playing!\n", delay=0.03, rich_style="bold green")

if __name__ == "__main__":
    intro = GameIntro()
    print("Starting the intro...")
    intro.play_intro()
    items_path = "d:\\Programming\\Codes\\Python\\AdventureGameProject\\items.json"
    game = AdventureGame("d:\\Programming\\Codes\\Python\\AdventureGameProject\\story.json", items_path)
    game.play_game()
    print("Game has exited successfully.")
    sys.exit(0)