from typing import Dict, List, TypedDict


class Room(TypedDict, total=False):
    description: str
    exits: Dict[str, str]
    items: List[str]
    puzzle: str
    puzzle_answer: str
    trap: bool
    trap_description: str


ROOMS: Dict[str, Room] = {
    "entrance": {
        "description": "Вы у входа в лабиринт. Впереди темный коридор.",
        "exits": {"north": "hall"},
        "items": [],
    },
    "hall": {
        "description": "Зал с факелами на стенах. На полу виднеется странная плита.",
        "exits": {"south": "entrance", "east": "treasure_room"},
        "items": ["key"],
        "trap": True,
        "trap_description": "Вы наступаете на плиту и слышите щелчок… ловушка!",
    },
    "trap_room": {
        "description": "Узкий коридор с мрачной атмосферой. "
        "В воздухе пахнет опасностью.",
        "exits": {"south": "hall"},
        "items": [],
        "trap": True,
        "trap_description": "Из-под ног уходит пол, и вы проваливаетесь вниз!",
    },
    "treasure_room": {
        "description": "Комната сокровищ. "
        "Перед вами тяжелая дверь с замочной скважиной.",
        "exits": {"west": "hall"},
        "items": ["treasure"],
        "puzzle": "На двери надпись: 'Что всегда идет, но никогда не приходит?'",
        "puzzle_answer": "завтра",
    },
}

AVAILABLE_COMMANDS = [
    "help",
    "look",
    "go",
    "inventory",
    "take",
    "use",
    "solve",
    "quit",
]

VICTORY_ITEM = "treasure"
KEY_ITEM = "key"

TRAP_CHANCE = 0.5
HEAL_EVENT_CHANCE = 0.3
HEAL_AMOUNT = 1

WELCOME_MESSAGE = "Добро пожаловать в 'Лабиринт сокровищ'!"
GOODBYE_MESSAGE = "Спасибо за игру!"
INVALID_COMMAND_MESSAGE = "Неизвестная команда. Введите 'help' для списка команд."
GAME_OVER_MESSAGE = "Игра уже завершена. Перезапустите, чтобы начать заново."
