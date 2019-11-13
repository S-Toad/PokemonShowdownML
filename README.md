# PokemonShowdownML

This project is WIP. The goal is to create a reinforcement learning AI for PokemonShowdown. Current plans are to contribute to another [showdown project](https://github.com/pmariglia/showdown) and adapt the existing code to create an environment for use in RL.

Regardless, this project still contains embeddings and other features that will be ported over to the final version.

## Files of Interest

### [battle.py](https://github.com/S-Toad/PokemonShowdownML/blob/master/state/battle.py)

It contains the main code for the environment. It mostly handles performing actions that will affect the state as well as listening for updates.

### [action.py](https://github.com/S-Toad/PokemonShowdownML/blob/master/state/action.py)

This file takes responsibility for storing operations done on the state of the game and handles encoding themselves using binary encoding. It directly handles parsing the text line given by the client.

### [team.py](https://github.com/S-Toad/PokemonShowdownML/blob/master/state/team.py)

Handles storing information about the player team. Its main job is determining whether an action is permissible given the current state.

