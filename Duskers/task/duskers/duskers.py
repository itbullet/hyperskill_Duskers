import json
import operator
from gamedata import GAME_TITLE, GAME_HUB, GAME_MENU, GAME_SAVED, GAME_LOADED, ROBOTS_1, ROBOTS_2, ROBOTS_3, ROBOTS_4, \
    UPGRADE_STORE, GAME_OVER, HELP_MESSAGE
import time
import random
import sys
import os
from datetime import datetime


class Duskers:

    def __init__(self, game_name: str, min_animation, max_animation, locations):
        self.game_name = game_name
        self.player_name = "guest"
        self.titanium = 0
        self.builtin_print = print
        self.min_animation = min_animation
        self.max_animation = max_animation
        self.locations_amount = 0
        self.number_of_robots = 3
        self.titanium_scan = 0
        self.enemy_encounter_scan = 0
        self.saved_games_dict = {}
        self.default_answers = []
        self.explorable_locations = []
        # self.locations = [location.replace(",", " ") for location in locations.split('/')]
        self.locations = [location.replace("_", " ") for location in locations.split(',')]
        self.menu_options = ["[New] Game", "[Load] Game", "[High] Scores", "[Help]", "[Exit]"]

    def wait_print_dot(self, min_wait, max_wait):
        current_time = int(time.time())
        wait_time = int(current_time % (max_wait - min_wait + 1) + min_wait)
        for i in range(wait_time):
            print(".", end="", flush=True)
            time.sleep(0.5)
        print()

    def random_number(self):
        current_time = int(time.time())
        return (current_time % (self.max_animation - self.min_animation + 1) + self.min_animation) / 10

    def print(self, *args, sep="", end="\n", sleep_time=0):
        for word in args:
            for char in word:
                self.builtin_print(char, sep=sep, end="")
                time.sleep(sleep_time)
            if end == "\n":
                print()

    def menu(self):
        self.print(self.game_name)
        self.print(*self.menu_options)
        return self.read_command(["new", "load", "exit", "high", "help"])

    def handle_exit_option(self):
        print("Thanks for playing, bye!")
        quit()
        # return False

    def read_command(self, commands):
        # print(commands)
        while True:
            self.print("\nYour command: ", end='')
            command = input().lower()
            if command in commands:
                return command
            print("Invalid input")

    def handle_play_option(self):
        self.print("\nEnter your name: ", end='')
        self.player_name = input()
        print(f"\nWelcome, commander {self.player_name}!")
        while True:
            print("Are you ready to begin?")
            print("[Yes]  [No] Return to Main[Menu]")
            choice = self.read_command(["yes", "no", "menu"])
            if choice == "yes":
                return self.play_game()
            if choice == "menu":
                return True
            print("How about now.")

    def save_score(self):
        if os.path.isfile('high_score.txt'):
            with open('high_score.txt', 'r+', encoding='utf-8') as file:
                contents = file.read()
                if len(contents):
                    score = json.loads(contents)
                else:
                    score = []
                score.append({'name': self.player_name, 'score': self.titanium})
                top_10 = sorted(score, key=lambda x: x['score'], reverse=True)[:10]
                file.seek(0)
                json.dump(top_10, file)
                file.truncate()
        else:
            with open('high_score.txt', 'w', encoding='utf-8') as file:
                score = [{'name': self.player_name, 'score': self.titanium}]
                json.dump(score, file)

    def handle_high_scores(self):
        if os.path.isfile('high_score.txt'):
            with open('high_score.txt', 'r+') as file:
                print('HIGH SCORES')
                contents = file.read()
                if len(contents):
                    dict_data = json.loads(contents)
                    high_scores_dict = sorted(dict_data, key=lambda x: x['score'], reverse=True)[:10]
                    for index, value in enumerate(high_scores_dict, 1):
                        print(f'({index}) {value.get("name")} {value.get("score")}')
        else:
            print('No high scores yet.')

        print("[Back]")
        choice = self.read_command(["back"])
        if choice == "back":
            return True
        else:
            return False

    def handle_help(self):
        print(HELP_MESSAGE)
        return True

    def handle_explore(self):
        self.locations_amount = random.randint(1, 9)
        self.explorable_locations = []
        self.default_answers = ["s", "back"]

        answer = True
        while answer:
            if self.locations_amount > 0:
                self.print("Searching", end="")
                self.wait_print_dot(self.min_animation, self.max_animation)
                self.explorable_locations.append(
                    [random.choice(self.locations), random.randint(10, 100), random.random()])
                index = 0
                for index, location_list in enumerate(self.explorable_locations):
                    titanium_amount_string = f': {location_list[1]}'
                    enemy_encounter_string = f' Encounter rate: {round(location_list[2] * 100)}%'
                    print(f"[{index + 1}] {location_list[0]}{titanium_amount_string if self.titanium_scan else ''}"
                          f"{enemy_encounter_string if self.enemy_encounter_scan else ''}")
                self.default_answers.append(str(index + 1))
                self.locations_amount = self.locations_amount - 1
                print("[S] to continue searching")
            else:
                print("Nothing more in sight.")
                print("[Back]")
                # return self.read_command(self.default_answers)
                # choice = self.read_command(self.default_answers)

            choice = self.read_command(self.default_answers)
            if choice == "s":
                answer = True
            elif choice == "back":
                # answer = False
                self.play_game()
            elif choice in self.default_answers:
                print("Deploying robots", end='')
                self.wait_print_dot(self.min_animation, self.max_animation)

                location_name = self.explorable_locations[int(choice) - 1][0]
                titanium_found = self.explorable_locations[int(choice) - 1][1]
                location_encounter_probability = self.explorable_locations[int(choice) - 1][2]
                encounter_probability = random.random()

                if encounter_probability >= location_encounter_probability:
                    print(f'{location_name}  explored successfully, with no damage taken.')
                else:
                    print(f'Enemy encounter!!!')
                    self.number_of_robots -= 1
                    if self.number_of_robots == 0:
                        print('Mission aborted, the last robot lost...')
                        #         save the result to highscore table if top 10
                        self.save_score()
                        print(GAME_OVER)
                        main()
                        print(f'{location_name}  explored successfully, 1 robot lost..')
                self.titanium += titanium_found
                print(f"Acquired {titanium_found} lumps of titanium")
                robots_number = self.amount_of_robots()
                print(GAME_HUB.format(robots_number, self.titanium))
                # return self.play_game()
                return True

    def handle_load(self):

        while True:
            print('\nSelect save slot:')
            if os.path.isfile('save_file.txt'):
                with open('save_file.txt', 'r', encoding='utf-8') as file:
                    saved_games_dict = json.load(file)
                    for i in list(['1', '2', '3']):
                        if saved_games_dict.get(i):
                            name = saved_games_dict[i][0]
                            titanium = saved_games_dict[i][1]
                            robots = saved_games_dict[i][2]
                            dt = saved_games_dict[i][3]

                            titanium_info = ''
                            if saved_games_dict.get(i)[4]:
                                titanium_info = 'titanium_info '
                            enemy_info = ''
                            if saved_games_dict.get(i)[5]:
                                enemy_info = 'enemy_info'
                            upgrades = f'{titanium_info}{enemy_info}'
                            self.print(
                                f'[{i}] {name} Titanium: {titanium} Robots: {robots} Last save: {dt} Upgrades: {upgrades}')
                        else:
                            self.print(f'[{i}] empty')

            else:
                for i in list(['1', '2', '3']):
                    self.print(f'[{i}] empty')

            choice = self.read_command(['back', '1', '2', '3'])

            if choice in list(['1', '2', '3']):
                if saved_games_dict.get(choice):
                    name = saved_games_dict.get(choice)[0]
                    self.player_name = name
                    self.titanium = saved_games_dict.get(choice)[1]
                    self.number_of_robots = saved_games_dict.get(choice)[2]
                    self.titanium_scan = saved_games_dict.get(choice)[4]
                    self.enemy_encounter_scan = saved_games_dict.get(choice)[5]
                    print(GAME_LOADED)
                    print(f'Welcome back, commander {name}!')
                    self.play_game()
                else:
                    print('Empty slot!')

            elif choice == 'back':
                return True

    def handle_save(self):
        print('Select save slot:')
        if os.path.isfile('save_file.txt'):
            with open('save_file.txt', 'r', encoding='utf-8') as file:
                contents = file.read()
                if len(contents):
                    saved_games_dict = json.loads(contents)
                else:
                    saved_games_dict = {}
                for i in list(['1', '2', '3']):
                    if saved_games_dict.get(i):
                        name = saved_games_dict.get(i)[0]
                        titanium = saved_games_dict.get(i)[1]
                        robots = saved_games_dict.get(i)[2]
                        dt = saved_games_dict.get(i)[3]

                        titanium_info = ''
                        if saved_games_dict.get(i)[4]:
                            titanium_info = 'titanium_info '
                        enemy_info = ''
                        if saved_games_dict.get(i)[5]:
                            enemy_info = 'enemy_info'
                        upgrades = f'{titanium_info}{enemy_info}'
                        self.print(f'[{i}] {name} Titanium: {titanium} Robots: {robots} Last save: {dt} Upgrades: {upgrades}')
                    else:
                        self.print(f'[{i}] empty')

        else:
            for i in list(['1', '2', '3']):
                self.print(f'[{i}] empty')

        choice = self.read_command(['back', '1', '2', '3'])

        if choice in list(['1', '2', '3']):
            dt_str = datetime.now().strftime('%Y-%m-%d %H:%M')
            if os.path.isfile('save_file.txt'):
                with open('save_file.txt', 'r+', encoding='utf-8') as file:
                    contents = file.read()
                    if len(contents):
                        self.saved_games_dict = json.loads(contents)
                    else:
                        self.saved_games_dict = {}

                    self.saved_games_dict[choice] = [self.player_name, self.titanium, self.number_of_robots, dt_str,
                                                     self.titanium_scan, self.enemy_encounter_scan]
                    file.seek(0)
                    json.dump(self.saved_games_dict, file)
                    file.truncate()
            else:
                with open('save_file.txt', 'w', encoding='utf-8') as file:
                    self.saved_games_dict.update(
                        {choice: [self.player_name, self.titanium, self.number_of_robots, dt_str, self.titanium_scan,
                                  self.enemy_encounter_scan]})
                    json.dump(self.saved_games_dict, file)
            print(GAME_SAVED)
            self.play_game()
        else:
            self.play_game()

    def handle_upgrade(self):
        print(UPGRADE_STORE)

        choice = self.read_command(['back', '1', '2', '3'])

        if choice == '1':
            if self.titanium >= 250:
                self.titanium_scan = 1
                self.titanium -= 250
                print('Purchase successful. You can now see how much titanium you can get from each found location.')
            else:
                print('Not enough titanium!')
            self.play_game()
        elif choice == '2':
            if self.titanium >= 500:
                self.enemy_encounter_scan = 1
                self.titanium -= 500
                print(
                    'Purchase successful. You will now see how likely you will encounter an enemy at each found location.')
            else:
                print('Not enough titanium!')
            self.play_game()
        elif choice == '3':
            if self.titanium >= 1000:
                if self.number_of_robots < 4: self.number_of_robots += 1
                self.titanium -= 1000
                print('Purchase successful. You now have an additional robot.')
            else:
                print('Not enough titanium!')
            self.play_game()
        elif choice == 'back':
            self.play_game()

    def handle_menu(self):
        print(GAME_MENU)
        return True

    def amount_of_robots(self):
        robots_dict = {
            1: ROBOTS_1,
            2: ROBOTS_2,
            3: ROBOTS_3,
            4: ROBOTS_4
        }
        return robots_dict.get(self.number_of_robots)

    def play_game(self):
        robots_number = self.amount_of_robots()
        print(GAME_HUB.format(robots_number, self.titanium))
        game_status = True
        while game_status:
            choice = self.read_command(["back", "m", "save", "exit", "ex", "up", "main"])
            if choice == 'back':
                self.play_game()
            elif choice == 'm':
                game_status = self.handle_menu()
            elif choice == 'save':
                self.handle_save()
            elif choice == 'exit':
                self.handle_exit_option()
            elif choice == 'ex':
                game_status = self.handle_explore()
            elif choice == 'up':
                self.handle_upgrade()
            elif choice == 'main':
                main()


def main():
    args = sys.argv
    if len(args) == 5:
        seed_number = args[1]
        min_animation = float(args[2])
        max_animation = float(args[3])
        locations = args[4]
    else:
        seed_number = "10"
        min_animation = 0
        max_animation = 0
        locations = "High_street,Green_park,Destroyed_Arch"

    random.seed(seed_number)
    game = Duskers(GAME_TITLE, min_animation, max_animation, locations)
    game_status = True
    actions = {
        "new": game.handle_play_option,
        "exit": game.handle_exit_option,
        "help": game.handle_help,
        "high": game.handle_high_scores,
        "ex": game.handle_explore,
        "save": game.handle_save,
        "load": game.handle_load,
        "up": game.handle_upgrade,
        "m": game.handle_menu
    }
    while game_status:
        menu_option = game.menu()
        game_status = actions[menu_option]()


if __name__ == "__main__":
    main()
