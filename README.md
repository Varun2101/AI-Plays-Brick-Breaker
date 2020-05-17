# AI-Plays-Brick-Breaker
Uses neural networks with NEAT to train on and beat the classic Atari game 'Breakout' aka Brick Breaker.

**NOTE:** There is randomness involved in the starting velocity and direction of the ball. Neural networks will often only optimize a part of these possible options, so **even Test_best_AI.py will do well only 50% of the time** despite putting together multiple neural networks. To get the perfect AI, train for more generations (default is at 300) after removing the fitness threshold from NEAT_config.txt, or create neural networks for each random option of the ball and put the best of each together. Note that this will likely take several hours (100 gens ~ 1hr) and hence hasn't been done yet.

### Requirements:
 * pygame
 * neat-python (ensure you install neat-python and not just neat)

### Instructions for use:
 * To play the game on your own, run game_env.py
 * To modify the fitness function and/or retrain the neural network, run Train_Brick_Breaker_AI.py
 * To run the pickled models, use Test_best_AI.py
 * To change the configuration of the NEAT neural networks, change the parameters in NEAT_config.txt
 * You can view the winning game from my fitness function in the .mp4 video
 * bestGenome.txt contains details of the winning neural network as reported by NEAT's stat reporter, but cannot be run directly. Use to see to details of the winning neural network.
