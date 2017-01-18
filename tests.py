#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

import game


class RecordTest(unittest.TestCase):
    def setUp(self):
        self.rec = game.Recorder()

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
        self.assertEqual(set(self.rec.players), {"L", "P", "S", "MG", "A"})


class PlayerTest(unittest.TestCase):
    def setUp(self):
        self.game = game.Game()

    def all_get_right_point(self, game, numbers, point):
        for num in numbers:
            self.assertEqual(game.get_point(num), point)

    def test_rec_str_process(self):
        self.assertEqual(self.game.process_record_str("P S MG A L"), ["P", "S", "MG", "A", "L"])
        self.assertEqual(self.game.process_record_str("P,   S,  MG, A,L,M,S，S"),
                                                      ["P", "S", "MG", "A", "L", "M", "S", "S"])

    def test_player_get_point_when_red_win(self):
        red_win_missions = [game.FAIL_MISSION for x in range(3)]
        self.game.add_record(["L", "P", "S", "MG", "A"], red_win_missions)
        self.all_get_right_point(self.game, [1,2,3], 0)
        self.all_get_right_point(self.game, [4,5], 1)

        self.game.add_record(["A", "L", "S", "MG", "P", "S"], red_win_missions)
        self.all_get_right_point(self.game, [1,4], 1)
        self.all_get_right_point(self.game, [2,3,6,5], 0)

    def test_player_get_point_when_blue_win(self):
        blue_win_missions = [game.SUCCESS_MISSION for x in range(3)]
        self.game.add_record(["S", "S", "A", "MG", "L", "O", "P"], blue_win_missions)
        self.all_get_right_point(self.game, [1,2,5,7], 1)
        self.all_get_right_point(self.game, [3,4,6], 0)


class GameHostTest(unittest.TestCase):
    def setUp(self):
        self.gh = game.GameHost()

    def test_basic_one_regular_game(self):
        game_id = self.gh.new_game(8, game.REGULAR)
        self.assertEqual(game_id, game.REGULAR)
        players = self.gh.get_game_players(game_id)
        self.roles_verify(players, 8)
        for num in range(8):
            self.play_get_role_ok(players, num+1)

    def test_role_assign_random_in_regular_game(self):
        for num in game.PLAYER_COUNT:
            for player_number in range(1, num+1):
                roles = []
                for n in range(num // 2 + 1):
                    game_id = self.gh.new_game(num, game.REGULAR)
                    players = self.gh.get_game_players(game_id)
                    roles.append(self.gh.get_role(player_number, game_id))
                self.assertTrue(len(set(roles)) >= 1)


    def play_get_role_ok(self, players, player_number):
        role = players[player_number]
        self.assertTrue(role in game.ROLES_FOR_NUMBER[len(players)])

    def roles_verify(self, players, number):
        self.assertEqual(len(players), number)
        self.assertEqual(sorted(players.values()), sorted(game.ROLES_FOR_NUMBER[number]))

    def test_get_right_roles_and_numbers(self):
        for num in game.PLAYER_COUNT:
            players = self.gh.get_game_players(self.gh.new_game(num))
            self.assertEqual(set(players.keys()), set(range(1, num+1)))

    def test_player_get_right_vision(self):
        for count in game.PLAYER_COUNT:
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
        self.assertListEqual(self.gh.get_vision(1, game_id), [5])
        self.assertListEqual(self.gh.get_vision(2, game_id), [1, 5])
        self.assertListEqual(self.gh.get_vision(3, game_id), [1, 2])
        self.assertFalse(self.gh.get_vision(4, game_id))
        self.assertListEqual(self.gh.get_vision(5, game_id), [1])

        self.gh.new_game(6, game_id)
        self.gh.set_players(game_id, ["S", "MG", "L", "P", "S", "A"])
        self.assertFalse(self.gh.get_vision(1, game_id))
        self.assertListEqual(self.gh.get_vision(2, game_id), [6])
        self.assertListEqual(self.gh.get_vision(3, game_id), [2, 6])
        self.assertListEqual(self.gh.get_vision(4, game_id), [2, 3])
        self.assertFalse(self.gh.get_vision(5, game_id))
        self.assertListEqual(self.gh.get_vision(6, game_id), [2])

        self.gh.new_game(7, game_id)
        self.gh.set_players(game_id, ["S", "MG", "L", "P", "S", "A", "O"])
        self.assertFalse(self.gh.get_vision(1, game_id))
        self.assertListEqual(self.gh.get_vision(2, game_id), [6])
        self.assertListEqual(self.gh.get_vision(3, game_id), [2, 6, 7])
        self.assertListEqual(self.gh.get_vision(4, game_id), [2, 3])
        self.assertFalse(self.gh.get_vision(5, game_id))
        self.assertListEqual(self.gh.get_vision(6, game_id), [2])
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