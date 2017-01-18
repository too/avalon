#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

import avalon


class RecordTest(unittest.TestCase):
    def setUp(self):
        self.recorder = avalon.Recorder()

    def tearDown(self):
        pass

    def test_red_win_with_3_fail(self):
        self.recorder.add_fail_mission(3)
        self.assertTrue(self.recorder.is_red_win())
        self.assertFalse(self.recorder.is_blue_win())

    def test_red_win_with_kill_merlin(self):
        self.recorder.set_kill_merlin()
        self.assertTrue(self.recorder.is_red_win())
        self.assertFalse(self.recorder.is_blue_win())

    def test_blue_win(self):
        self.recorder.add_success_mission(3)
        self.assertTrue(self.recorder.is_blue_win())
        self.assertFalse(self.recorder.is_red_win())

    def test_game_points(self):
        self.recorder.add_fail_mission()
        self.assertEqual(self.recorder.get_points(), "0:1")
        self.recorder.add_fail_mission(1)
        self.assertEqual(self.recorder.get_points(), "0:2")
        self.recorder.add_success_mission()
        self.assertEqual(self.recorder.get_points(), "1:2")
        self.recorder.add_success_mission(2)
        self.assertEqual(self.recorder.get_points(), "3:2")

    def test_rules_of_blue_red(self):
        self.recorder.set_players(["L", "P", "S", "MG", "A"])
        self.assertEqual(len(self.recorder.players), 5)
        self.assertEqual(set(self.recorder.players), {"L", "P", "S", "MG", "A"})

    def all_get_right_point(self, recorder, numbers, point):
        for num in numbers:
            self.assertEqual(recorder.get_player_point(num), point)

    def test_rec_str_process(self):
        self.assertEqual(self.recorder.process_record_str("P S MG A L"), ["P", "S", "MG", "A", "L"])
        self.assertEqual(self.recorder.process_record_str("P,   S,  MG, A,L,M,S，S"),
                         ["P", "S", "MG", "A", "L", "M", "S", "S"])

    def test_player_get_point_when_red_win(self):
        red_win_missions = [avalon.FAIL_MISSION for x in range(3)]
        self.recorder.add_record(["L", "P", "S", "MG", "A"], red_win_missions)
        self.all_get_right_point(self.recorder, [1, 2, 3], 0)
        self.all_get_right_point(self.recorder, [4, 5], 1)

        self.recorder.__init__()
        self.recorder.set_kill_merlin()
        self.recorder.add_record(["A", "L", "S", "MG", "P", "S"],
                                 [avalon.SUCCESS_MISSION for x in range(3)])
        self.all_get_right_point(self.recorder, [1, 4], 1)
        self.all_get_right_point(self.recorder, [2, 3, 6, 5], 0)

    def test_player_get_point_when_blue_win(self):
        blue_win_missions = [avalon.SUCCESS_MISSION for x in range(3)]
        self.recorder.add_record(["S", "S", "A", "MG", "L", "O", "P"], blue_win_missions)
        self.all_get_right_point(self.recorder, [1, 2, 5, 7], 1)
        self.all_get_right_point(self.recorder, [3, 4, 6], 0)


class GameTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_basic_one_regular_game(self):
        g = avalon.Game(8, avalon.REGULAR)
        self.assertEqual(g.id, avalon.REGULAR)
        self.roles_verify(g.roles, 8)
        for role in g.roles:
            self.assertTrue(role in avalon.ROLES_FOR_NUMBER[8])

    def roles_verify(self, roles, number):
        self.assertEqual(len(roles), number)
        self.assertItemsEqual(roles, avalon.ROLES_FOR_NUMBER[number])

    def test_role_assign_random_in_regular_game(self):
        for num in avalon.PLAYER_COUNT:
            for player_number in range(1, num+1):
                play_get_roles = []
                for n in range(num // 2 + 1):
                    g = avalon.Game(num, avalon.REGULAR)
                    play_get_roles.append(g.role_for(player_number))
                self.assertTrue(len(set(play_get_roles)) >= 1)

    def test_get_right_roles_and_numbers(self):
        for num in avalon.PLAYER_COUNT:
            game = avalon.Game(num)
            self.assertItemsEqual([p.number for p in game.players], range(1, num+1))

    def visions_verify(self, game, number_visions):
        for number, visions in number_visions:
            player = game.players[number-1]
            self.assertListEqual(player.visions, visions)

    def test_player_get_right_vision(self):
        for count in avalon.PLAYER_COUNT:
            game = avalon.Game(count)
            for p in game.players:
                if p.role in game.roles_have_vision:
                    self.assertTrue(p.visions)
                else:
                    self.assertFalse(p.visions)
        game = avalon.Game(5)
        game.set_roles_to_player(["MG", "L", "P", "S", "A"])
        self.visions_verify(game, ((1, [5]),
                                   (2, [1, 5]),
                                   (3, [1, 2]),
                                   (5, [1]),
                                   (4, [])))
        game = avalon.Game(6)
        game.set_roles_to_player(["S", "MG", "L", "P", "S", "A"])
        self.visions_verify(game, ((1, []),
                                   (2, [6]),
                                   (3, [2, 6]),
                                   (4, [2, 3]),
                                   (5, []),
                                   (6, [2])))
        game = avalon.Game(7)
        game.set_roles_to_player(["S", "MG", "L", "P", "S", "A", "O"])
        self.visions_verify(game, ((1, []),
                                   (2, [6]),
                                   (3, [2, 6, 7]),
                                   (4, [2, 3]),
                                   (5, []),
                                   (6, [2]),
                                   (7, [])))
        game = avalon.Game(8, show_grade=True)
        game.set_roles_to_player(["S", "M", "L", "P", "S", "MG", "A", "S"])
        self.visions_verify(game, ((1, []),
                                   (2, [6, 7]),
                                   (3, [2, 6, 7]),
                                   (4, [3, 6]),
                                   (6, [7, 2]),
                                   (7, [6, 2])))
        game = avalon.Game(9, show_grade=True)
        game.set_roles_to_player(["S", "MG", "L", "S", "P", "S", "MD", "A", "S"])
        self.visions_verify(game, ((4, []),
                                   (2, [7, 8]),
                                   (3, [2, 8]),
                                   (5, [2, 3]),
                                   (7, [2, 8]),
                                   (8, [7, 2])))
        game = avalon.Game(10, show_grade=True)
        game.set_roles_to_player(["S", "MG", "L", "S", "O", "P", "S", "MD", "A", "S"])
        self.visions_verify(game, ((1, []),
                                   (2, [8, 9]),
                                   (3, [2, 5, 9]),
                                   (6, [2, 3]),
                                   (8, [2, 9]),
                                   (9, [8, 2])))
