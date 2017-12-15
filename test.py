from run_game import GameRunner

verbose = "n"
x_player = "better_player"
o_player = "simple_player"
k = 5
time_per_k_turns = 100
setup_time = 5

runner_x_first = GameRunner(setup_time, time_per_k_turns, k, verbose, x_player, o_player)

runner_o_first = GameRunner(setup_time, time_per_k_turns, k, verbose, o_player, x_player)

print("X random starts 3 times:")
for round in range(3):
    runner_x_first.run()

print("X simple starts 3 times:")
for round in range(3):
    runner_o_first.run()
