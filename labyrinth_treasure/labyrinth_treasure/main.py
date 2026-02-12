from typing import List

from .constants import (
    GAME_OVER_MESSAGE,
    GOODBYE_MESSAGE,
    INVALID_COMMAND_MESSAGE,
    WELCOME_MESSAGE,
)
from .player_actions import (
    look,
    move_player,
    show_inventory,
    solve_puzzle,
    take_item,
    use_item,
)
from .utils import parse_command, print_welcome, show_help


def main() -> None:
    current_room = "entrance"
    inventory: List[str] = []
    health = 3
    game_over = False
    victory = False
    door_unlocked = False
    solved_main_puzzle = False

    print(WELCOME_MESSAGE)
    print_welcome()
    look(current_room)

    while True:
        user_input = input("> ")
        command, args = parse_command(user_input)

        if not command:
            continue

        if game_over:
            print(GAME_OVER_MESSAGE)
            if command == "quit":
                print(GOODBYE_MESSAGE)
                break
            continue

        if command == "help":
            show_help()

        elif command == "look":
            look(current_room)

        elif command == "inventory":
            show_inventory(inventory)

        elif command == "go":
            if not args:
                print("Укажите направление (например, 'go north').")
                continue
            direction = args[0]
            current_room, health, trap_triggered = move_player(
                current_room,
                direction,
                health,
            )
            if health <= 0:
                game_over = True
                print(GAME_OVER_MESSAGE)
                print(GOODBYE_MESSAGE)
                break

            look(current_room)

        elif command == "take":
            if not args:
                print("Укажите предмет, который хотите взять.")
                continue
            item_name = args[0]
            take_item(current_room, inventory, item_name)

        elif command == "use":
            if not args:
                print("Укажите предмет, который хотите использовать.")
                continue
            item_name = args[0]
            door_changed, victory_flag = use_item(
                current_room,
                inventory,
                item_name,
                solved_main_puzzle,
            )
            if door_changed:
                door_unlocked = True
            if victory_flag:
                victory = True
                game_over = True
                print(GAME_OVER_MESSAGE)
                print(GOODBYE_MESSAGE)
                break

        elif command == "solve":
            if not args:
                print("Введите ответ на загадку после 'solve'.")
                continue
            answer = " ".join(args)
            solved_main_puzzle = solve_puzzle(
                current_room,
                answer,
                solved_main_puzzle,
            )

        elif command == "quit":
            print(GOODBYE_MESSAGE)
            break

        else:
            print(INVALID_COMMAND_MESSAGE)

        if not game_over:
            print(f"HP: {health}")

        if current_room == "treasure_room" and door_unlocked and not victory:
            print(
                "Перед вами открытый проход наружу. "
                "Используйте сокровище, чтобы победить.",
            )


if __name__ == "__main__":
    main()
