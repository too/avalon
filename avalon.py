#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import random
from datetime import datetime

RED_WIN = FAIL_MISSION = 0
BLUE_WIN = SUCCESS_MISSION = 1
# MAX_NUMBER_OF_MISSION = 5
BLUE_ROLES = ("L", "P", "S")
PLAYER_COUNT = (5, 6, 7, 8, 9, 10)
ROLES_FOR_NUMBER = {5: ["MG", "A", "L", "P", "S"],
                    6: ["MG", "A", "L", "P", "S", "S"],
                    7: ["MG", "A", "O", "L", "P", "S", "S"],
                    8: ["MG", "A", "M", "L", "P", "S", "S", "S"],
                    9: ["MG", "A", "MD", "L", "P", "S", "S", "S", "S"],
                    10: ["MG", "A", "MD", "O", "L", "P", "S", "S", "S", "S"],
                    }

RED_GRADE = ("MD", "MG", "A", "M")
ROLE_VISION = {"L": ("MG", "A", "M", "O"),
               "P": ("MG", "L"),
               }
for v in RED_GRADE:
    ROLE_VISION[v] = RED_GRADE

NEWBIE = 1
REGULAR = 2
BACKUP = 3
DEFAULT_GAME_IDS = (NEWBIE, REGULAR, BACKUP)


class Recorder(object):
    def __init__(self):
        self.missions = []
        self.kill_merlin = False
        self.players = None
        self.red_player_numbers = []
        self.blue_player_numbers = []

    def get_points(self):
        return "{}:{}".format(self.missions.count(SUCCESS_MISSION),
                              self.missions.count(FAIL_MISSION))

    def add_missions(self, num, status):
        for x in range(num):
            self.missions.append(status)

    def add_fail_mission(self, num=1):
        self.add_missions(num, FAIL_MISSION)

    def add_success_mission(self, num=1):
        self.add_missions(num, SUCCESS_MISSION)

    def set_kill_merlin(self):
        self.kill_merlin = True

    def is_red_win(self):
        return self.kill_merlin or (self.missions.count(FAIL_MISSION) == 3)

    def is_blue_win(self):
        return not self.kill_merlin and (self.missions.count(SUCCESS_MISSION) == 3)

    def divide_player_numbers(self):
        for number, role in enumerate(self.players, 1):
            if role in BLUE_ROLES:
                self.blue_player_numbers.append(number)
            else:
                self.red_player_numbers.append(number)

    def set_players(self, players):
        self.players = players
        self.divide_player_numbers()

    @staticmethod
    def process_record_str(rec_str):
        ret = rec_str.replace(",", " ").replace("，", " ")
        return ret.split()

    def add_record(self, players, missions):
        self.set_players(players)
        self.add_fail_mission(missions.count(FAIL_MISSION))
        self.add_success_mission(missions.count(SUCCESS_MISSION))
        
    def get_player_point(self, number):
        if self.is_red_win():
            if number in self.red_player_numbers:
                return 1
            else:
                return 0
        elif self.is_blue_win():
            if number in self.blue_player_numbers:
                return 1
            else:
                return 0


class Player(object):

    def __init__(self, number, role, game_id):
        self.number = number
        self.role = role
        self.game_id = game_id
        self.visions = None



class Game(object):

    def __init__(self, count, game_id=REGULAR, show_grade=False):
        self.roles = ROLES_FOR_NUMBER[count]
        self.id = game_id
        self.start = False
        self.created = datetime.now()
        self.show_grade = show_grade
        self.players = None
        self.roles_have_vision = None
        random.shuffle(self.roles)
        self.setup_player()

    def setup_player(self):
        self.roles_have_vision = [role for role in self.roles
                                  if role in ROLE_VISION.keys()]
        players = []
        for num, role in enumerate(self.roles, 1):
            player = Player(num, role, self.id)
            player.visions = self.get_vision_for(num, role)
            players.append(player)
        self.players = players

    def set_roles_to_player(self, roles):
        self.roles = roles
        self.setup_player()

    def role_for(self, number):
        return self.roles[number-1]

    def get_player(self, number):
        return self.players[number-1]

    def get_vision_for(self, player_number, role):
        can_see_role = ROLE_VISION.get(role, [])
        vd = {}
        for number, num_role in enumerate(self.roles, 1):
            if num_role in can_see_role:
                vd[number] = num_role
        vd.pop(player_number, None)
        ret = vd.keys()
        if self.show_grade and (len(self.roles) >= 8) and role in RED_GRADE:
            def red_sort(x, y):
                return cmp(RED_GRADE.index(vd[x]), RED_GRADE.index(vd[y]))
            ret.sort(cmp=red_sort)
        else:
            ret.sort()
        return ret


class GameHost(object):
    def __init__(self):
        self.games = {}
        self.count = 0
        self.game_ids = []
        self.roles_have_vision = ROLE_VISION.keys()

    def gen_game_id(self):
        new_id = random.randrange(50, 10000)
          
    def new_game(self, number, game_id=None, show_grade=False):
        game_id = game_id or self.gen_game_id()
        player_roles = self.gen_roles(number)
        game = {"start": True, "created": datetime.now(), "show_grade": show_grade}
        self.games[game_id] = game
        self.set_players(game_id, player_roles)
        return game_id