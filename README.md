# AI Racer

A 2D top-down racing game built with **Pygame** where you draw your own track by hand, then train a **Deep Q-Network (DQN)** to drive it — with up to 50 cars learning in parallel off a single shared "hive-mind" brain.

You can also just drive it yourself.

## Features

- **Freehand track editor** — draw the track, checkpoints, drift zones, and finish line straight onto the canvas with the mouse.
- **Manual driving mode** — drive a single car with the keyboard, with drifting and speed-boost mechanics.
- **AI training mode** — spin up 50 cars at once, all learning from a shared replay buffer and shared network (DQN with a target network and epsilon-greedy exploration).
- **Flying lap mode** — drop down to a single car at real-time speed to watch the current policy drive, without leaving training mode.
- **Raycast-based perception** — each car casts 7 distance rays to "see" the track edges, feeding a small neural network.
- **Lap timing & leaderboard HUD** — live fastest / average / slowest lap stats while training.
- **Save / load checkpoints** — persist the trained model (weights, optimizer state, epsilon, step count) to disk.

## Requirements

- Python 3.10+
- [PyTorch](https://pytorch.org/) (CUDA optional — falls back to CPU automatically)
- [Pygame](https://www.pygame.org/)

```bash
pip install torch pygame
```

## Running it

```bash
python main.py
```

The game opens directly into **Draw mode**, where you sketch your track before switching to **Drive mode**.

## Controls

### Draw mode

| Key | Action |
|---|---|
| Left click + drag | Draw the current brush (track, checkpoint, or drift-zone) |
| `E` | Toggle edit menu (brush/tool selection) |
| `C` | Clear the whole track |
| `M` | Switch to Drive mode |

**Edit menu (press `E` first):**

| Key | Action |
|---|---|
| `1` / `2` / `3` | Large / medium / small track brush |
| `4` | Place a manual checkpoint at the cursor |
| `5` | Drift-zone brush |
| `6` | Clear-drift-zone brush |
| `0` | Clear all checkpoints |

> The very first click of a session sets the car's spawn point and the finish line.

### Drive mode

| Key | Action |
|---|---|
| `M` | Back to Draw mode |
| `T` | Toggle between AI training (50 cars) and manual driving (1 car) |
| `F` | Toggle flying-lap mode — **training mode only** |
| `I` | Toggle ray visualization |
| `K` | Save the current model to `model.pth` |
| `L` | Load a saved model from `model.pth` |
| `P` | Print all recorded lap times to the console |

**Manual driving (when AI training is off):**

| Key | Action |
|---|---|
| `W` / `↑` | Accelerate |
| `S` / `↓` | Reverse / brake |
| `A` / `←` | Steer left |
| `D` / `→` | Steer right |
| `Space` / `Right Shift` | Drift |

## How the AI works

Each car perceives the world through **10 raycasts** (fired at different angles from the nose of the car and 3 from the bottom) plus its own **normalized speed** and **heading angle** — a 12-value state vector fed into a small fully-connected network:

```
Input (12) → 128 → 128 → 128 → Output (13 Q-values)
```

The 13 discrete actions cover coasting, gas, brake, left/right, combinations of gas/brake with steering, and several drift variants.

All cars in training mode share **one policy network, one target network, and one replay buffer** — every car's experience feeds the same brain, so 50 cars effectively generate 50x the training data per frame. The network is trained with standard DQN:

- Epsilon-greedy exploration, decaying over time
- A separate target network, synced periodically for stable targets
- Reward shaping for: forward speed, staying on track, drifting inside drift zones, passing checkpoints in order, and completing a lap
- Large penalties for crashing or crossing the finish line the wrong way

## Project structure

```
.
├── main.py          # Game loop, UI, input handling, mode switching
├── car.py            # Car physics, sprite rendering, raycasting, drift/boost logic
├── track_drawer.py   # Track canvas: drawing, checkpoints, drift zones, finish-line detection
├── Model.py           # DQN network, replay buffer, training loop, reward function
└── model.pth          # Saved model weights (created after you press K)
```

## Tips

- Draw a track with generous width — tight tracks make it harder for the AI to stay on the racing line early in training.
- Training runs uncapped (as fast as your CPU/GPU allows) unless flying-lap mode is on, which caps it to 60 FPS so you can actually watch a lap in real time.
- The code has an auto checkpoints placer by default but it is not the best so after drawing the track i suggest you that
- you enter the edit mode of the drawing and clear all the checkpoints and place new one manually.
- 50 cars might be a bit too much or not enough depending on your CPU/GPU so go too {line 27} in the {main.py} and change the number to what ever feels right too you.
  
