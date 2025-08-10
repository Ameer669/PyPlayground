# Adventure Game Extension Plan

## I. Core Mechanic Enhancements (AdventureGame.py)

- [X] **A. Crafting System**
  - [X] 1. Implement `can_craft(recipe_name)` function.
  - [X] 2. Implement `craft_item(recipe_name)` function.
  - [X] 3. Integrate crafting option into game loop (e.g., at specific locations or as a general action).
- [X] **B. Item Durability System**
  - [X] 1. Modify combat to reduce weapon durability on attack and armor durability when hit.
  - [X] 2. Define behavior for items at 0 durability (break and remove, or become unusable).
  - [X] 3. (Optional) Add items/mechanics for repairing durable items.
- [X] **C. Special Item Effects/Abilities**
  - [X] 1. Implement `shadow_cloak` ("stealth") functionality (e.g., modify enemy detection, flee chance, first strike).
  - [X] 2. Implement `antidote` ("cure_poison") functionality.
  - [X] 3. Implement `glowing_crystal` ("light_radius") functionality for dark areas.
- [X] **D. Status Effects (Player)**
  - [X] 1. Implement `player_status` dictionary (e.g., `{"poisoned": {"active": true, "duration": 3, "damage_per_turn": 5}}`).
  - [X] 2. Implement poison effect (e.g., damage over time).
  - [X] 3. Modify game loop to check and apply status effects.

## II. Content Expansion (story.json & items.json)

- [X] **A. `right_path` - The Abandoned Mine**
  - [X] 1. Add new story nodes for the Abandoned Mine branch in `story.json`.
  - [X] 2. Add new items (`pickaxe`, `iron_ore`, `ancient_gear`, `miner_helmet`) to `items.json`.
  - [X] 3. Add new enemies (`giant_cave_spider`, `mine_foreman_ghost`) to `story.json` (and potentially `items.json` for drops).
- [X] **B. `next_adventure_node` - The Whispering Woods & Ancient Ruins**
  - [X] 1. Add new story nodes for this branch in `story.json`.
  - [X] 2. Introduce NPC (Old Hermit) with a simple quest.
  - [X] 3. Add new items (`hermit_amulet`, `ancient_tablet`, `stone_sword`, `elixir_of_wisdom`) to `items.json`.
  - [X] 4. Add new enemies (`stone_guardian`, `forest_spirit`) to `story.json`.
- [X] **C. Crafting Expansion (items.json)**
  - [X] 1. Add new crafting recipes (`iron_ingot`, `reinforced_shield`, `healing_salve`, `poison_darts`).
  - [X] 2. Add new crafting materials/components (`cloth`, `iron_ingot` (as item), `spider_venom`).
- [X] **D. General Story Polish**
  - [X] 1. Expand the `end` node in `story.json` for varied endings.
  - [X] 2. Add more descriptive text to existing nodes in `story.json`.
  - [X] 3. Introduce more choices with meaningful consequences in `story.json`.

## III. Library & Asset Management

- [X] **A. Sound Effects**
  - [X] 1. Identify or note the need for new sound effects (crafting, item breaking, new enemy actions, puzzle solving, new consumables).
  - [X] 2. (Optional) Integrate placeholders if actual sound files are not immediately available.
- [X] **B. Python Libraries**
  - [X] 1. Confirm existing libraries are sufficient.

## IV. Testing and Validation

- [X] **A. Thoroughly test extended game**
  - [X] 1. Test all new story branches.
  - [X] 2. Test new mechanics (crafting, durability, special effects, status effects).
  - [X] 3. Test new items and enemies.
- [X] **B. Validate gameplay and functionality**
  - [X] 1. Ensure game balance with new additions.
  - [X] 2. Check for bugs, crashes, or unintended behaviors.
  - [X] 3. Verify all choices lead to appropriate outcomes.

## V. Finalization

- [X] **A. Update game version in `story.json`**
- [X] **B. Ensure all files are correctly saved and packaged.**

