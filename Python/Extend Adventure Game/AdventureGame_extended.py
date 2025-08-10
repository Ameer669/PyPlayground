import time  # time delay
import random  # random number generation
import json  # JSON file handling
import sys  # text delay
import os # For os.path.exists and os.system
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
            # Play all scenes, not just title_screen
            screen.play(scenes, stop_on_resize=False, repeat=False)

        finally:
            screen.close()

    def play_intro(self):
        try:
            Screen.wrapper(self.intro)
        except Exception as e:
            print(f"Error running intro screen: {e}")
        finally:
            # Reset terminal state thoroughly
            print("\033[0m", end="")      # Reset colors
            print("\033[?25h", end="")    # Show cursor
            print("\033[?1049l", end="")  # Exit alternate buffer (if used by asciimatics)
            print("\033[2J", end="")      # Clear screen
            print("\033[H", end="")       # Move cursor to top-left
            sys.stdout.flush()            # Force output
            print("", flush=True) # Additional reset for Windows terminals


class AdventureGame:
    def __init__(self, story_file, items_file="items.json"):
        with open(story_file, 'r') as f:
            self.story = json.load(f)
        with open(items_file, 'r') as f:
            self.items_data = json.load(f)

        self.all_items = {}
        for category_name, category_items in self.items_data["items"].items():
            if isinstance(category_items, dict):
                self.all_items.update(category_items)
            else:
                print(f"Warning: Category '{category_name}' is not a dictionary of items.")

        self.crafting_recipes = self.items_data.get("crafting_recipes", {})

        self.current = "start"
        self.hp = self.story.get("player", {}).get("hp", 100)
        self.base_attack_power = random.randint(12, 20) # Default if not in story
        self.base_defense_power = 5 # Default if not in story
        self.equipped_items = []
        self.inventory = []
        self.time_of_day = "day"
        self.player_status = {}
        pygame.mixer.init()
        
        try:
            self.find_item_sound = pygame.mixer.Sound("mixkit-fast-sword-whoosh-2792.wav")
            self.craft_sound = pygame.mixer.Sound("craft_success.wav")
            self.item_break_sound = pygame.mixer.Sound("item_break.wav")
        except pygame.error as e:
            print(f"Warning: Could not load sound files: {e}")
            self.find_item_sound = None
            self.craft_sound = None
            self.item_break_sound = None
        self.console = Console()

    def type_text(self, text, delay=0.05, rich_style=""):
        for char in text:
            self.console.print(Text(char, style=rich_style), end="")
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
        try:
            os.system("cls" if os.name == "nt" else "clear")
            print("\033[?25h", end="") 
            print("\033[0m", end="") 
        except:
            pass

    def get_attack_power(self):
        bonus = sum(item.get("attack_bonus", 0) for item in self.equipped_items if item.get("durability", 1) > 0)
        return self.base_attack_power + bonus

    def get_defense_bonus(self):
        bonus = sum(item.get("defense_bonus", 0) for item in self.equipped_items if item.get("durability", 1) > 0)
        return self.base_defense_power + bonus

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

    def use_item_durability(self, item_type):
        for item in self.equipped_items[:]: # Iterate over a copy for safe removal
            if item_type == "weapon" and "attack_bonus" in item:
                item["durability"] = item.get("durability", 100) - 1
                if item["durability"] <= 0:
                    self.type_text(f"Your {item['name']} broke!", rich_style="bold red")
                    self.play_sound(self.item_break_sound)
                    self.equipped_items.remove(item)
                break 
            elif item_type == "armor" and "defense_bonus" in item:
                item["durability"] = item.get("durability", 100) - 1
                if item["durability"] <= 0:
                    self.type_text(f"Your {item['name']} broke!", rich_style="bold red")
                    self.play_sound(self.item_break_sound)
                    self.equipped_items.remove(item)
                break 

    def toggle_time_of_day(self, node):
        if node.get("make_night", False):
            self.time_of_day = "night"
            self.type_text(Fore.LIGHTMAGENTA_EX + "\nStars twinkle above as darkness falls." + Style.RESET_ALL, delay=0.05)
            time.sleep(0.5)
            self.type_text(Fore.LIGHTMAGENTA_EX + "\nIt is now night." + Style.RESET_ALL, delay=0.05)
        elif node.get("make_day", False):
            self.time_of_day = "day"
            self.type_text(Fore.LIGHTMAGENTA_EX + "\nSunlight spills over the horizon." + Style.RESET_ALL, delay=0.05)
            time.sleep(0.5)
            self.type_text(Fore.LIGHTMAGENTA_EX + "\nIt is now day." + Style.RESET_ALL, delay=0.05)

    def get_validated_input(self, prompt_text, valid_choices):
        while True:
            try:
                self.console.print(prompt_text, end="", style="yellow")
                raw_input_text = input().strip()
                choice = int(raw_input_text)
                if choice in valid_choices:
                    return choice
                else:
                    self.console.print(f"\nPlease select a valid option from {', '.join(map(str, valid_choices))}.\n", style="red")
                    time.sleep(0.5)
            except ValueError:
                self.console.print("\nPlease enter a valid number.\n", style="red")
                time.sleep(0.5)
            except KeyboardInterrupt:
                self.console.print("\nGame interrupted. Exiting...\n", style="red")
                self.current = "end"
                self.cleanup()
                sys.exit(0)

    def combat(self, enemy_key):
        enemy_data = self.story["enemies"][enemy_key]
        enemy_hp = enemy_data["hp"]
        enemy_defense = enemy_data.get("defense", 0)
        enemy_attack_range = enemy_data["attack_range"]
        miss_chance = 0.3 if self.time_of_day == "night" else 0.1

        first_strike = False
        if any(item.get("name") == "Shadow Cloak" and item.get("special_ability") == "stealth" for item in self.equipped_items):
            miss_chance *= 0.5 
            if random.random() < 0.5: 
                first_strike = True
                self.type_text("Your Shadow Cloak allows you to strike first!", rich_style="bold green")

        while enemy_hp > 0 and self.hp > 0:
            self.console.print(Panel(f"Combat: You are fighting {enemy_data['name']}!", style="bold red", border_style="red"))
            time.sleep(0.5)
            stats_table = Table()
            stats_table.add_column("You", style="blue")
            stats_table.add_column("Enemy", style="red")
            
            current_player_attack = self.get_attack_power()
            display_min_attack = current_player_attack - (current_player_attack // 10) 
            display_max_attack = current_player_attack + (current_player_attack // 10)

            stats_table.add_row(f"HP: {self.hp}", f"HP: {enemy_hp}")
            stats_table.add_row(f"Attack: {display_min_attack}-{display_max_attack}", f"Attack: {enemy_attack_range[0]}-{enemy_attack_range[1]}")
            stats_table.add_row(f"Defense: {self.get_defense_bonus()}", f"Defense: {enemy_defense}")
            self.console.print(stats_table)
            self.console.print(f"Miss Chance: {miss_chance * 100:.0f}% (Your Stealth: {first_strike})", style="yellow")
            time.sleep(0.5)

            player_turn_options = {"1": "Attack", "2": "Use Item", "3": "Flee"}
            
            if first_strike:
                self.type_text("You take the initiative!", rich_style="green")
                pass
            
            self.console.print("Options:", style="yellow")
            for k, v in player_turn_options.items():
                self.console.print(f"{k}. {v}", style="yellow")
            
            choice = self.get_validated_input("Your choice: ", [1, 2, 3])
            self.console.rule(style="white")

            if choice == 1: 
                if random.random() < miss_chance:
                    time.sleep(1)
                    self.type_text("You missed your attack!", delay=0.03, rich_style="red")
                else:
                    actual_player_attack = random.randint(current_player_attack - (current_player_attack//10), current_player_attack + (current_player_attack//10))
                    damage_to_enemy = max(0, actual_player_attack - enemy_defense)
                    enemy_hp -= damage_to_enemy
                    self.use_item_durability("weapon")
                    time.sleep(1)
                    self.type_text(Fore.LIGHTGREEN_EX + f"You deal {damage_to_enemy} damage to the {enemy_data['name']}." + Style.RESET_ALL, delay=0.03, rich_style="green")
                    if enemy_hp <= 0:
                        time.sleep(1)
                        self.type_text(Fore.LIGHTGREEN_EX + f"You defeated {enemy_data['name']}!" + Style.RESET_ALL, delay=0.03, rich_style="green")
                        # Add loot
                        if "loot" in enemy_data:
                            for loot_item_key in enemy_data["loot"]:
                                if loot_item_key in self.all_items:
                                    self.inventory.append(self.all_items[loot_item_key].copy())
                                    self.type_text(f"You found: {self.all_items[loot_item_key]['name']}", rich_style="yellow")
                        return "win"
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
                    self.type_text(Fore.BLUE + f"\nYou successfully fled from {enemy_data['name']}."+ Style.RESET_ALL, delay=0.05)
                    time.sleep(1)
                    return "flee"
                else:
                    time.sleep(1)
                    self.type_text(Fore.RED + f"You failed to flee from {enemy_data['name']}!"+ Style.RESET_ALL, delay=0.05, rich_style="yellow")
            
            first_strike = False

            if enemy_hp > 0 and (choice != 3 or random.random() >= flee_success_chance):
                enemy_attack = random.randint(*enemy_attack_range)
                player_defense_val = self.get_defense_bonus()
                damage_to_player = max(0, enemy_attack - player_defense_val)
                self.hp -= damage_to_player
                self.use_item_durability("armor")
                self.type_text(Fore.RED + f"The {enemy_data['name']} deals {damage_to_player} damage to you."+ Style.RESET_ALL, delay=0.03)
                if self.hp <= 0:
                    time.sleep(1)
                    self.type_text(Fore.RED + "\nYou were defeated!\n"+ Style.RESET_ALL, delay=0.07)
                    time.sleep(1)
                    return "lose"
            
            self.apply_status_effects()
            if self.hp <= 0:
                 self.type_text("You succumbed to your ailments!", rich_style="bold red")
                 return "lose"

        if enemy_hp <= 0: 
            return "win"
        return "ongoing" 

    def can_craft(self, recipe_name):
        if recipe_name not in self.crafting_recipes:
            return False
        recipe = self.crafting_recipes[recipe_name]
        inventory_item_names_temp = [item["name"] for item in self.inventory]
        for required_item_name, quantity in recipe["required_items"].items():
            if inventory_item_names_temp.count(required_item_name) < quantity:
                return False
        return True

    def craft_item(self, recipe_name):
        if not self.can_craft(recipe_name):
            self.type_text("You don't have the required materials or the recipe is unknown.", rich_style="red")
            return

        recipe = self.crafting_recipes[recipe_name]
        for required_item_name, quantity_needed in recipe["required_items"].items():
            removed_count = 0
            for item_in_inv in self.inventory[:]:
                if item_in_inv["name"] == required_item_name and removed_count < quantity_needed:
                    self.inventory.remove(item_in_inv)
                    removed_count += 1
        
        crafted_item_key = recipe["result_key"]
        if crafted_item_key in self.all_items:
            self.inventory.append(self.all_items[crafted_item_key].copy())
            self.type_text(f"You successfully crafted: {self.all_items[crafted_item_key]['name']}!", rich_style="bold green")
            self.play_sound(self.craft_sound)
        else:
            self.type_text(f"Error: Crafted item key '{crafted_item_key}' not found in item database.", rich_style="red")

    def open_crafting_menu(self):
        self.console.print(Panel("Crafting Menu", style="bold yellow", border_style="yellow"))
        available_crafts_map = {}
        display_idx = 1
        self.type_text("Available recipes you can craft:", rich_style="cyan")
        for recipe_name, recipe_data in self.crafting_recipes.items():
            if self.can_craft(recipe_name):
                req_str = ", ".join([f"{qty}x {itemName}" for itemName, qty in recipe_data["required_items"].items()])
                result_item_name = self.all_items.get(recipe_data["result_key"], {}).get("name", recipe_data["result_key"])
                self.type_text(f"{display_idx}. {recipe_name} (Requires: {req_str}) -> {result_item_name}", rich_style="green")
                available_crafts_map[display_idx] = recipe_name
                display_idx += 1
        
        if not available_crafts_map:
            self.type_text("You cannot craft anything with your current items or known recipes.", rich_style="yellow")
            return

        self.type_text(f"{display_idx}. Exit Crafting", rich_style="cyan")
        
        choice = self.get_validated_input("Choose a recipe to craft (number): ", list(range(1, display_idx + 1)))
        
        if choice in available_crafts_map:
            self.craft_item(available_crafts_map[choice])
        elif choice == display_idx:
            self.type_text("Exiting crafting menu.", rich_style="yellow")

    def open_inventory(self, in_combat=False):
        if not self.inventory:
            self.console.print("You have no items in your inventory!", style="yellow")
            return
        while True:
            time.sleep(0.1)
            self.console.print("")
            table = Table(title="Inventory", border_style="cyan", style="green")
            table.add_column("#", style="cyan")
            table.add_column("Name", style="magenta")
            table.add_column("Type", style="green")
            table.add_column("Info", style="yellow")
            table.add_column("Durability", style="blue")

            for i, item in enumerate(self.inventory, 1):
                name = item['name']
                item_type = item['type']
                info_str = "N/A"
                if "attack_bonus" in item: info_str = f"ATK: +{item['attack_bonus']}"
                elif "defense_bonus" in item: info_str = f"DEF: +{item['defense_bonus']}"
                elif "hp_restore" in item: info_str = f"HP: +{item['hp_restore']}"
                elif "effect" in item: info_str = f"Effect: {item['effect']}"
                elif "special_ability" in item: info_str = f"Ability: {item['special_ability']}"
                elif "light_radius" in item: info_str = f"Light: {item['light_radius']}"
                
                durability = item.get("durability", "-")
                table.add_row(str(i), name, item_type, str(info_str), str(durability))

            self.console.print(table)
            time.sleep(0.1)
            self.console.print(f"\n{len(self.inventory) + 1}. Exit Inventory", style="cyan")

            try:
                choice_idx = self.get_validated_input("Choose an item (number) or exit: ",
                                                  list(range(1, len(self.inventory) + 2))) - 1
                if 0 <= choice_idx < len(self.inventory):
                    selected_item = self.inventory[choice_idx]
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
                            self.inventory.pop(choice_idx)
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
                                        # self.inventory.append(eq_item) # Add old item back to general inventory
                                        break # Break after unequipped one, then equip new one
                            
                            if can_equip:
                                self.equipped_items.append(selected_item)
                                self.inventory.pop(choice_idx)
                                self.type_text(f"You equipped {selected_item['name']}.", style="yellow")
                    else:
                        self.type_text(f"{selected_item['name']} is a {selected_item['type']} item. {selected_item.get('description', '')}", style="cyan")
                elif choice_idx == len(self.inventory):
                    self.type_text("Exiting inventory...", delay=0.03, rich_style="yellow")
                    break
            except ValidationError:
                pass 

    def body(self):
        self.console.print(Panel("Equipped Items", style="bold magenta", border_style="magenta"))
        if not self.equipped_items:
            self.type_text("You have nothing equipped.", rich_style="yellow")
            return

        for i, item in enumerate(self.equipped_items, 1):
            durability_info = f" (Dur: {item.get('durability', '-')})" if "durability" in item else ""
            self.type_text(f"{i}. {item['name']} ({item['type']}){durability_info} - {item.get('description', '')}", rich_style="cyan")
        
        self.type_text(f"\n{len(self.equipped_items) + 1}. Back", rich_style="cyan")
        choice = self.get_validated_input("View details or go back: ", list(range(1, len(self.equipped_items) + 2)))
        if choice == len(self.equipped_items) + 1:
            return
        else: 
            self.type_text("Returning to game.", rich_style="yellow")
            time.sleep(1)

    def handle_choice(self, choice_data):
        if "condition" in choice_data:
            required_items_names = choice_data["condition"]
            inventory_item_names_temp = [item["name"] for item in self.inventory]
            has_all_required = True
            temp_inventory_for_check = inventory_item_names_temp[:]
            for req_item_name in required_items_names:
                if req_item_name in temp_inventory_for_check:
                    temp_inventory_for_check.remove(req_item_name)
                else:
                    has_all_required = False
                    break
            
            if not has_all_required:
                self.type_text(f"You don't have the required items: {', '.join(required_items_names)}!", rich_style="red")
                return self.current 

            # If condition met, remove items from actual inventory
            for req_item_name in required_items_names:
                for item_obj in self.inventory[:]: 
                    if item_obj["name"] == req_item_name:
                        self.inventory.remove(item_obj)
                        break 
            self.type_text(f"You used: {', '.join(required_items_names)} to proceed!", rich_style="yellow")

        self.current = choice_data["node"]
        self.hp = min(100, self.hp + choice_data.get("hp_change", 0))
        if self.hp <= 0:
            self.type_text("Your journey ends here... Game Over.", rich_style="bold red")
            return "end"
        return self.current

    def clear_terminal(self):
        time.sleep(0.05) 
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def display_node_info(self, node):
        self.clear_terminal()
        self.console.rule(style="white")
        time.sleep(0.1)
        text_to_display = node['text']
        panel_style = "bold cyan"
        
        # Check for light source for dark areas
        has_light_source = False
        for item in self.inventory + self.equipped_items:
            if item.get("special_ability") in ["light_source_small", "light_source_medium", "light_source_strong"] and item.get("durability", 1) > 0:
                has_light_source = True
                break
        
        is_dark_area_node = "dark_area_description" in node

        if is_dark_area_node and not has_light_source:
            text_to_display = node["dark_area_description"]
            panel_style = "dim white on black" # Style for dark areas
        
        self.console.print(Panel(text_to_display, title=node.get("node_title", "Location"), style=panel_style, border_style="blue"))
        time.sleep(0.1)
        
        if "strength_boost" in self.player_status and self.player_status["strength_boost"]["active"]:
            self.type_text(f"(Strength Boost Active: {self.player_status['strength_boost']['duration']} turns left)", rich_style="yellow")
        if "poisoned" in self.player_status and self.player_status["poisoned"]["active"]:
            self.type_text(f"(Poisoned: {self.player_status['poisoned']['duration']} turns left)", rich_style="red")

    def sleep(self):
        self.type_text("You decide to rest for a while...", rich_style="yellow")
        time.sleep(2)
        hp_gain = random.randint(10, 25)
        self.hp = min(100, self.hp + hp_gain)
        self.type_text(f"You feel rested and recover {hp_gain} HP. Current HP: {self.hp}", rich_style="green")
        self.time_of_day = "day" # Sleeping makes it day
        self.type_text("The sun is rising. It is now day.", rich_style="yellow")
        # Clear temporary status effects like strength boost on sleep
        if "strength_boost" in self.player_status: self.player_status.pop("strength_boost")
        time.sleep(1)

    def play_game(self):
        found_items_in_nodes = set()
        slept_in_current_node = False

        initial_inventory_keys = self.story.get("player", {}).get("inventory", [])
        for item_key in initial_inventory_keys:
            if item_key in self.all_items:
                self.inventory.append(self.all_items[item_key].copy())
                self.type_text(f"You start with: {self.all_items[item_key]['name']}", rich_style="yellow")
            else:
                self.type_text(f"Warning: Initial inventory item '{item_key}' not found.", rich_style="red")

        while self.current != "end" and self.hp > 0:
            node = self.story.get(self.current)
            if not node:
                self.type_text(f"Error: Node '{self.current}' not found. Ending game.", rich_style="bold red")
                self.current = "end"
                break

            if not slept_in_current_node:
                self.toggle_time_of_day(node)
            slept_in_current_node = False

            self.display_node_info(node)
            self.apply_status_effects()
            if self.hp <= 0 or self.current == "end": break

            if "items" in node:
                for item_key in node["items"]:
                    if f"{self.current}_{item_key}" not in found_items_in_nodes:
                        if item_key in self.all_items:
                            item_to_add = self.all_items[item_key].copy()
                            self.inventory.append(item_to_add)
                            found_items_in_nodes.add(f"{self.current}_{item_key}")
                            self.type_text(Fore.LIGHTGREEN_EX + f"You found: {item_to_add['name']}" + Style.RESET_ALL, delay=0.03)
                            self.play_sound(self.find_item_sound)
                            time.sleep(0.5)
                        else:
                            self.type_text(f"Warning: Item key '{item_key}' in node '{self.current}' not found in item database.", rich_style="red")
            
            if self.time_of_day == "night" and "sleep_choices" in node:
                self.type_text("It is night. You can choose to sleep or keep moving.", rich_style="yellow")
                self.type_text("1. Sleep", rich_style="cyan")
                self.type_text("2. Keep moving", rich_style="cyan")
                sleep_choice_input = self.get_validated_input("Your choice: ", [1, 2])
                if sleep_choice_input == 1:
                    self.sleep()
                    slept_in_current_node = True 
                    if self.hp <= 0 or self.current == "end": break
                    self.current = node["sleep_choices"].get("sleep_node", self.current) 
                    continue 
                else: 
                    self.current = node["sleep_choices"].get("move_node", self.current)
                    node = self.story.get(self.current)
                    if not node: self.current = "end"; break
                    self.display_node_info(node)

            choices = node.get("choices", {})
            if not choices:
                if self.current != "end":
                    self.type_text("There are no more paths from here. The adventure ends.", rich_style="yellow")
                    self.current = "end"
                continue

            self.console.rule(style="white")
            self.type_text(f"Your HP: {self.hp}", delay=0.03, rich_style="green")
            self.type_text(f"Attack Power: {self.get_attack_power()}", delay=0.03, rich_style="blue")
            self.type_text(f"Defense: {self.get_defense_bonus()}", delay=0.03, rich_style="blue")
            time.sleep(0.2)
            
            self.type_text("\nChoices:", delay=0.03, rich_style="bold yellow")
            choice_keys = list(choices.keys())
            for i, choice_text in enumerate(choice_keys, 1):
                self.type_text(f"{i}. {choice_text}", delay=0.03, rich_style="cyan")
            
            action_options_start_index = len(choice_keys) + 1
            possible_actions = {
                action_options_start_index: "Open Inventory",
                action_options_start_index + 1: "See Equipped Items",
                action_options_start_index + 2: "Craft Items"
            }
            for i, action_text in possible_actions.items():
                 self.type_text(f"{i}. {action_text}", delay=0.03, rich_style="yellow")

            valid_input_range = list(range(1, action_options_start_index + len(possible_actions)))
            self.console.print("\nSelect an option by entering the number.", style="white")
            raw_choice_num = self.get_validated_input("Your choice: ", valid_input_range)

            if 1 <= raw_choice_num <= len(choice_keys):
                chosen_text_key = choice_keys[raw_choice_num - 1]
                choice_data = choices[chosen_text_key]
                
                if choice_data["type"] == "combat":
                    enemy_key = choice_data["enemy_key"]
                    outcome = self.combat(enemy_key)
                    if outcome == "win":
                        self.current = choice_data["win_node"]
                    elif outcome == "flee":
                        self.current = choice_data["flee_node"]
                    else: 
                        self.current = "end"
                else: 
                    self.current = self.handle_choice(choice_data)
            elif raw_choice_num == action_options_start_index : 
                self.open_inventory()
            elif raw_choice_num == action_options_start_index + 1:
                self.body()
            elif raw_choice_num == action_options_start_index + 2:
                self.open_crafting_menu()
            
            if self.hp <= 0 and self.current != "end":
                self.type_text("You have succumbed to your wounds! Game Over.", delay=0.03, rich_style="bold red")
                self.current = "end"
            time.sleep(0.2)

        self.cleanup()
        self.console.rule(style="white")
        final_text = self.story.get("end", {}).get("text", "The adventure ends here.")
        if self.hp <=0 and self.current == "end":
            final_text = self.story.get("death_end", {}).get("text", "You have died. Your adventure is over.")
        self.type_text(final_text, delay=0.03, rich_style="bold cyan")
        self.type_text("\nThank you for playing!\n", delay=0.03, rich_style="bold green")

if __name__ == "__main__":
    story_file_path = "D:\Programming\Codes\Python\Extend Adventure Game\story_extended.json" 
    items_file_path = "D:\Programming\Codes\Python\Extend Adventure Game\items_extended.json"
    
    placeholder_sounds = ["craft_success.wav", "item_break.wav", "mixkit-fast-sword-whoosh-2792.wav"]
    for sound_f in placeholder_sounds:
        if not os.path.exists(sound_f):
            try:
                with open(sound_f, 'w') as pf: pf.write("")
                print(f"Created placeholder sound file: {sound_f}")
            except Exception as e_sound:
                print(f"Could not create placeholder sound {sound_f}: {e_sound}")

    #intro = GameIntro()
    #print("Starting the intro...")
    #intro.play_intro() # Optional, can be problematic

    print(f"Loading story from: {os.path.abspath(story_file_path)}")
    print(f"Loading items from: {os.path.abspath(items_file_path)}")

    if not os.path.exists(story_file_path):
        print(f"Error: Story file not found at {story_file_path}")
        sys.exit(1)
    if not os.path.exists(items_file_path):
        print(f"Error: Items file not found at {items_file_path}")
        sys.exit(1)
    
    try:
        game = AdventureGame(story_file_path, items_file_path)
        game.cleanup()
        game.play_game()
    except KeyboardInterrupt:
        print("\nGame interrupted by user. Exiting.")
        game.cleanup()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        game.cleanup()
    finally:
        print("Game has exited.")
        sys.exit(0)

