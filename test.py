from run_game import GameRunner

verbose = "n"
x_player = "random_player"
o_player = "simple_player"
k = 5
time_per_k_turns = 10
setup_time = 1

runner_x_first = GameRunner(setup_time, time_per_k_turns, k, verbose, x_player, o_player)

runner_o_first = GameRunner(setup_time, time_per_k_turns, k, verbose, o_player, x_player)

for round in range(3):
    runner_x_first.run()
for round in range(3):
    runner_o_first.run()

print("hey")

