import unittest


RED_WIN = FAIL_MISSION = 0
BLUE_WIN = SUCCESS_MISSION = 1
MAX_NUMBER_OF_MISSION = 5
RED_ROLES = ("MG", "MD", "M", "A", "O")

class Record(object):
    def __init__(self):
        self.missions = []
        self.kill_merlin = False
        self.players = None
        self.red_player_numbers = []
        self.blue_player_numbers = []

    def get_points(self):
        return "{}:{}".format(self.missions.count(1), self.missions.count(0))

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
            if role in RED_ROLES:
                self.red_player_numbers.append(number)
            else:
                self.blue_player_numbers.append(number)
        
    def set_players(self, players):
        self.players = players
        self.divide_player_numbers()

class Game():
    def __init__(self):
        self.rec = None


    def add_record(self, players, missions):
        self.rec = Record()
        self.rec.set_players(players)
        self.rec.add_missions(missions.count(FAIL_MISSION), FAIL_MISSION)
        self.rec.add_missions(missions.count(SUCCESS_MISSION), SUCCESS_MISSION)
        
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
        self.rec.add_fail_mission(2)
        self.assertEqual(self.rec.get_points(), "0:2")
        self.rec.add_success_mission(3)
        self.assertEqual(self.rec.get_points(), "3:2")

    def test_rules_of_blue_red(self):
        self.rec.set_players(["L", "P", "S", "MG", "A"])
        self.assertEqual(len(self.rec.players), 5)
        self.assertEqual(set(self.rec.players), set(["L", "P", "S", "MG", "A"]))

class PlayerTest(unittest.TestCase):
    def setUp(self):
        self.game = Game()
    
    def all_get_point(self, game, numbers, point):
        for num in numbers:
            self.assertEqual(game.get_point(num), point)

    def test_player_get_point_when_red_win(self):
        red_win_missions = [FAIL_MISSION for x in range(3)]
        self.game.add_record(["L", "P", "S", "MG", "A"], red_win_missions)
        self.all_get_point(self.game, [1,2,3], 0)
        self.all_get_point(self.game, [4,5], 1)
        
        self.game.add_record(["A", "L", "S", "MG", "P", "S"], red_win_missions)
        self.all_get_point(self.game, [1,4], 1)
        self.all_get_point(self.game, [2,3,6,5], 0)
    
    def test_player_get_point_when_blue_win(self):
        blue_win_missions = [SUCCESS_MISSION for x in range(3)]
        self.game.add_record(["S", "S", "A", "MG", "L", "O", "P"], blue_win_missions)
        self.all_get_point(self.game, [1,2,5,7], 1)
        self.all_get_point(self.game, [3,4,6], 0)



if __name__ == '__main__':
    unittest.main()
