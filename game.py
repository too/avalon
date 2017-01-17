
# -*- coding: utf-8 -*- #
from datetime import datetime
import random
import unittest


RED_WIN = FAIL_MISSION = 0
BLUE_WIN = SUCCESS_MISSION = 1
#MAX_NUMBER_OF_MISSION = 5
BLUE_ROLES = ("L", "P", "S")
PLAYER_COUNT = (5, 6, 7, 8, 9, 10)
ROLES_FOR_NUMBER = {
    5: ["MG", "A", "L", "P", "S"],
    6: ["MG", "A", "L", "P", "S", "S"],
    7: ["MG", "A", "O", "L", "P", "S", "S"],
    8: ["MG", "A", "M", "L", "P", "S", "S", "S"],
    9: ["MG", "A", "MD", "L", "P", "S", "S", "S", "S"],
    10: ["MG", "A", "MD", "O", "L", "P", "S", "S", "S", "S"],
}

RED_GRADE = ("MD", "MG", "A", "M")
ROLE_VISION = {
    "L": ("MG", "A", "M", "O"),
    "P": ("MG", "L"),
}
for v in RED_GRADE:
    ROLE_VISION[v] = RED_GRADE

NEWBIE = 1
REGULAR = 2
BACKUP = 3
DEFAULT_GAME_IDS = (NEWBIE, REGULAR, BACKUP)

class Record(object):
    def __init__(self):
        self.missions = []
        self.kill_merlin = False
        self.players = None
        self.red_player_numbers = []
        self.blue_player_numbers = []

    def get_points(self):
        return "{}:{}".format(self.missions.count(SUCCESS_MISSION), self.missions.count(FAIL_MISSION))

    def add_missions(self, num, status):
        for x in range(num):
            self.missions.append(status)

    def add_fail_mission(self, num=1):
        self.add_missions(num, FAIL_MISSION)

    def add_success_mission(self, num=1):
        self.add_missions(num, SUCCESS_MISSION)

    def is_kill_merlin(self):
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

class Game(object):
    def __init__(self):
        self.rec = None

    def process_record_str(self, rec_str):
        ret = rec_str.replace(",", " ").replace("，", " ")
        return ret.split()

    def add_record(self, players, missions):
        self.rec = Record()
        self.rec.set_players(players)
        self.rec.add_fail_mission(missions.count(FAIL_MISSION))
        self.rec.add_success_mission(missions.count(SUCCESS_MISSION))
        
    def get_point(self, number):
        if self.rec.is_red_win():
            if number in self.rec.red_player_numbers:
                return 1
            else:
                return 0
        elif self.rec.is_blue_win():
            if number in self.rec.blue_player_numbers:
                return 1
            else:
                return 0


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

    def set_players(self, game_id, player_roles):
        self.games[game_id]["players"] = {num: role for num, role in enumerate(player_roles, 1)}

    def gen_roles(self, number):
        roles = ROLES_FOR_NUMBER[number]
        random.shuffle(roles)
        return roles

    def get_game_players(self, game_id):
        return self.games[game_id]["players"]

    def get_role(self, player_number, game_id):
        players = self.get_game_players(game_id)
        return players[player_number]

    def have_vision(self, player_number, game_id):
        return self.get_role(player_number, game_id) in self.roles_have_vision

    def get_vision(self, player_number, game_id):
        players = self.get_game_players(game_id)
        role = self.get_role(player_number, game_id)
        can_see_role = ROLE_VISION.get(role, [])
        vd = {}
        for number, num_role in players.items():
            if num_role in can_see_role:
                vd[number] = num_role
        vd.pop(player_number, None)
        ret = self.get_sorted_player_numbers(vd, game_id, role)
        return ret

    def get_sorted_player_numbers(self, vd, game_id, role):
        ret = vd.keys()
        game = self.games[game_id]
        if game["show_grade"] and (len(game["players"]) >= 8) and role in RED_GRADE:
            def red_sort(x, y):
                return cmp(RED_GRADE.index(vd[x]), RED_GRADE.index(vd[y]))
            ret.sort(cmp=red_sort)
        else:
            ret.sort()
        return ret
        

class RecordTest(unittest.TestCase):
    def setUp(self):
        self.rec = Record()

    def tearDown(self):
        pass

    def test_red_win_with_3_fail(self):
        self.rec.add_fail_mission(3)
        self.assertTrue(self.rec.is_red_win())
        self.assertFalse(self.rec.is_blue_win())

    def test_red_win_with_kill_merlin(self):
        self.rec.is_kill_merlin()
        self.assertTrue(self.rec.is_red_win())
        self.assertFalse(self.rec.is_blue_win())

    def test_blue_win(self):
        self.rec.add_success_mission(3)
        self.assertTrue(self.rec.is_blue_win())
        self.assertFalse(self.rec.is_red_win())

    def test_game_points(self):
        self.rec.add_fail_mission()
        self.assertEqual(self.rec.get_points(), "0:1")        
        self.rec.add_fail_mission(1)
        self.assertEqual(self.rec.get_points(), "0:2")
        self.rec.add_success_mission()
        self.assertEqual(self.rec.get_points(), "1:2")
        self.rec.add_success_mission(2)
        self.assertEqual(self.rec.get_points(), "3:2")

    def test_rules_of_blue_red(self):
        self.rec.set_players(["L", "P", "S", "MG", "A"])
        self.assertEqual(len(self.rec.players), 5)
        self.assertEqual(set(self.rec.players), set(["L", "P", "S", "MG", "A"]))

class PlayerTest(unittest.TestCase):
    def setUp(self):
        self.game = Game()
    
    def all_get_right_point(self, game, numbers, point):
        for num in numbers:
            self.assertEqual(game.get_point(num), point)

    def test_rec_str_process(self):
        self.assertEqual(self.game.process_record_str("P S MG A L"), ["P", "S", "MG", "A", "L"])
        self.assertEqual(self.game.process_record_str("P,   S,  MG, A,L,M,S，S"),
                                                      ["P", "S", "MG", "A", "L", "M", "S", "S"])

    def test_player_get_point_when_red_win(self):
        red_win_missions = [FAIL_MISSION for x in range(3)]
        self.game.add_record(["L", "P", "S", "MG", "A"], red_win_missions)
        self.all_get_right_point(self.game, [1,2,3], 0)
        self.all_get_right_point(self.game, [4,5], 1)
        
        self.game.add_record(["A", "L", "S", "MG", "P", "S"], red_win_missions)
        self.all_get_right_point(self.game, [1,4], 1)
        self.all_get_right_point(self.game, [2,3,6,5], 0)
    
    def test_player_get_point_when_blue_win(self):
        blue_win_missions = [SUCCESS_MISSION for x in range(3)]
        self.game.add_record(["S", "S", "A", "MG", "L", "O", "P"], blue_win_missions)
        self.all_get_right_point(self.game, [1,2,5,7], 1)
        self.all_get_right_point(self.game, [3,4,6], 0)


class GameHostTest(unittest.TestCase):
    def setUp(self):
        self.gh = GameHost()

    def test_basic_one_regular_game(self):
        game_id = self.gh.new_game(8, REGULAR)
        self.assertEqual(game_id, REGULAR)
        players = self.gh.get_game_players(game_id)
        self.roles_verify(players, 8)
        for num in range(8):
            self.play_get_role_ok(players, num+1)

    def test_role_assign_random_in_regular_game(self):
        for num in PLAYER_COUNT:
            for player_number in range(1, num+1):
                roles = []
                for n in range(num // 2 + 1):
                    game_id = self.gh.new_game(num, REGULAR)
                    players = self.gh.get_game_players(game_id)
                    roles.append(self.gh.get_role(player_number, game_id))
                self.assertTrue(len(set(roles)) >= 1)
                

    def play_get_role_ok(self, players, player_number):
        role = players[player_number]
        self.assertTrue(role in ROLES_FOR_NUMBER[len(players)])

    def roles_verify(self, players, number):
        self.assertEqual(len(players), number)
        self.assertEqual(sorted(players.values()), sorted(ROLES_FOR_NUMBER[number]))

    def test_get_right_roles_and_numbers(self):
        for num in PLAYER_COUNT:
            players = self.gh.get_game_players(self.gh.new_game(num))
            self.assertEqual(set(players.keys()), set(range(1, num+1)))

    def test_player_get_right_vision(self):
        for count in PLAYER_COUNT:
            game_id = self.gh.new_game(count)
            players = self.gh.get_game_players(game_id)
            for number, role in players.items():
                vd = self.gh.get_vision(number, game_id)
                if self.gh.have_vision(number, game_id):
                    self.assertTrue(vd)
                else:
                    self.assertFalse(vd)
        game_id = 33
        self.gh.new_game(5, game_id)
        self.gh.set_players(game_id, ["MG", "L", "P", "S", "A"])
        self.assertListEqual(self.gh.get_vision(1, game_id), [5,])
        self.assertListEqual(self.gh.get_vision(2, game_id), [1, 5])
        self.assertListEqual(self.gh.get_vision(3, game_id), [1, 2])
        self.assertFalse(self.gh.get_vision(4, game_id))
        self.assertListEqual(self.gh.get_vision(5, game_id), [1,])
        
        self.gh.new_game(6, game_id)
        self.gh.set_players(game_id, ["S", "MG", "L", "P", "S", "A"])
        self.assertFalse(self.gh.get_vision(1, game_id))
        self.assertListEqual(self.gh.get_vision(2, game_id), [6,])
        self.assertListEqual(self.gh.get_vision(3, game_id), [2, 6])
        self.assertListEqual(self.gh.get_vision(4, game_id), [2, 3])
        self.assertFalse(self.gh.get_vision(5, game_id))
        self.assertListEqual(self.gh.get_vision(6, game_id), [2,])

        self.gh.new_game(7, game_id)
        self.gh.set_players(game_id, ["S", "MG", "L", "P", "S", "A", "O"])
        self.assertFalse(self.gh.get_vision(1, game_id))
        self.assertListEqual(self.gh.get_vision(2, game_id), [6,])
        self.assertListEqual(self.gh.get_vision(3, game_id), [2, 6, 7])
        self.assertListEqual(self.gh.get_vision(4, game_id), [2, 3])
        self.assertFalse(self.gh.get_vision(5, game_id))
        self.assertListEqual(self.gh.get_vision(6, game_id), [2,])
        self.assertFalse(self.gh.get_vision(7, game_id))

        self.gh.new_game(8, game_id, show_grade=True)
        self.gh.set_players(game_id, ["S", "M", "L", "P", "S", "MG", "A", "S"])
        self.assertFalse(self.gh.get_vision(1, game_id))
        self.assertListEqual(self.gh.get_vision(2, game_id), [6, 7])
        self.assertListEqual(self.gh.get_vision(6, game_id), [7, 2])
        self.assertListEqual(self.gh.get_vision(7, game_id), [6, 2])
        self.assertListEqual(self.gh.get_vision(3, game_id), [2, 6, 7])
        self.assertListEqual(self.gh.get_vision(4, game_id), [3, 6])

        self.gh.new_game(9, game_id, show_grade=True)
        self.gh.set_players(game_id, ["S", "MG", "L", "S", "P", "S", "MD", "A", "S"])
        self.assertFalse(self.gh.get_vision(1, game_id))
        self.assertListEqual(self.gh.get_vision(2, game_id), [7, 8])
        self.assertListEqual(self.gh.get_vision(7, game_id), [2, 8])
        self.assertListEqual(self.gh.get_vision(8, game_id), [7, 2])
        self.assertListEqual(self.gh.get_vision(3, game_id), [2, 8])
        self.assertListEqual(self.gh.get_vision(5, game_id), [2, 3])

        self.gh.new_game(10, game_id, show_grade=True)
        self.gh.set_players(game_id, ["S", "MG", "L", "S", "O", "P", "S", "MD", "A", "S"])
        self.assertFalse(self.gh.get_vision(1, game_id))
        self.assertFalse(self.gh.get_vision(5, game_id))
        self.assertListEqual(self.gh.get_vision(2, game_id), [8, 9])
        self.assertListEqual(self.gh.get_vision(8, game_id), [2, 9])
        self.assertListEqual(self.gh.get_vision(9, game_id), [8, 2])
        self.assertListEqual(self.gh.get_vision(3, game_id), [2, 5, 9])
        self.assertListEqual(self.gh.get_vision(6, game_id), [2, 3])


if __name__ == '__main__':
    unittest.main()
