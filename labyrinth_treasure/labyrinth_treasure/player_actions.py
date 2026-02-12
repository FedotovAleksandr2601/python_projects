import random
from typing import List, Tuple

from .constants import (
    HEAL_AMOUNT,
    HEAL_EVENT_CHANCE,
    KEY_ITEM,
    ROOMS,
    TRAP_CHANCE,
    VICTORY_ITEM,
)


def look(current_room: str) -> None:
    room = ROOMS[current_room]
    print(room["description"])

    items = room.get("items", [])
    if items:
        print(f"Вы видите: {', '.join(items)}")

    exits = room.get("exits", {})
    if exits:
        directions = ", ".join(exits.keys())
        print(f"Выходы: {directions}")

    if "puzzle" in room:
        print("Здесь есть загадка. Используйте команду 'solve'.")


def show_inventory(inventory: List[str]) -> None:
    if not inventory:
        print("Ваш инвентарь пуст.")
        return
    print("В вашем инвентаре:")
    print(", ".join(inventory))


def move_player(
    current_room: str,
    direction: str,
    health: int,
) -> Tuple[str, int, bool]:
    room = ROOMS[current_room]
    exits = room.get("exits", {})

    if direction not in exits:
        print("Вы не можете идти в этом направлении.")
        return current_room, health, False

    next_room = exits[direction]
    next_room_data = ROOMS[next_room]

    trap_triggered = False

    # Ловушки по комнатам
    if next_room_data.get("trap"):
        # Ловушка в trap_room: телепорт в entrance
        if next_room == "trap_room":
            if random.random() < TRAP_CHANCE:
                print(next_room_data.get("trap_description", "Срабатывает ловушка!"))
                print("Вы падаете и оказываетесь у входа в лабиринт.")
                health -= 1
                trap_triggered = True
                if health <= 0:
                    print("Вы погибли в ловушке.")
                # телепорт обратно на вход
                return "entrance", health, trap_triggered
            else:
                print("Вы осторожно двигаетесь вперед и избегаете ловушки.")
        else:
            # Обычная ловушка (например, в hall) с шансом
            if random.random() < TRAP_CHANCE:
                print(next_room_data.get("trap_description", "Срабатывает ловушка!"))
                health -= 1
                trap_triggered = True
                if health <= 0:
                    print("Вы погибли в ловушке.")
            else:
                print("Вы осторожно обходите подозрительное место и избегаете ловушки.")

    # Случайные события в hall, если ловушка не сработала
    if next_room == "hall" and not trap_triggered:
        roll = random.random()
        if roll < HEAL_EVENT_CHANCE:
            print("Вы находите забытое зелье лечения и чувствуете прилив сил.")
            health += HEAL_AMOUNT
        elif roll < HEAL_EVENT_CHANCE + 0.2:
            print("Сквозняк задувает факелы, пламя на мгновение тускнеет.")
            print("На несколько секунд вы едва различаете контуры стен.")

    return next_room, health, trap_triggered

def take_item(current_room: str, inventory: List[str], item_name: str) -> None:
    room_items = ROOMS[current_room].get("items", [])
    if item_name not in room_items:
        print("Здесь нет такого предмета.")
        return

    room_items.remove(item_name)
    inventory.append(item_name)
    print(f"Вы подняли: {item_name}")


def use_item(
    current_room: str,
    inventory: List[str],
    item_name: str,
    solved_main_puzzle: bool,
) -> Tuple[bool, bool]:
    if item_name not in inventory:
        print("У вас нет этого предмета.")
        return False, False

    if current_room == "treasure_room" and item_name == KEY_ITEM:
        print("Вы вставляете ключ в замок. Дверь открывается.")
        return True, False

    if item_name == VICTORY_ITEM and solved_main_puzzle:
        print("Вы использовали сокровище и выбрались из лабиринта. Победа!")
        return False, True

    print("Предмет нельзя использовать здесь.")
    return False, False


def solve_puzzle(
    current_room: str,
    user_answer: str,
    solved_main_puzzle: bool,
) -> bool:
    room = ROOMS[current_room]
    puzzle = room.get("puzzle")
    if not puzzle:
        print("Здесь нет загадки.")
        return solved_main_puzzle

    correct_answer = room.get("puzzle_answer", "").lower()
    if user_answer.strip().lower() == correct_answer:
        print("Вы разгадали загадку!")
        if current_room == "treasure_room":
            return True
        return solved_main_puzzle

    print("Неверный ответ на загадку.")
    return solved_main_puzzle
