
import torch
import torch.nn as nn
import torch.nn.functional as F
import random
from collections import deque

# ---------- 1. HYPERPARAMETERS (adjust as you like) ----------
INPUT_SIZE = 10          # number of ray distances
ACTION_SIZE = 10         
GAMMA = 0.99
LEARNING_RATE = 0.001
BATCH_SIZE = 250
REPLAY_CAPACITY = 50000
TARGET_UPDATE = 100     # steps between target network updates
EPS_START = 1.0
EPS_END = 0.01
EPS_DECAY = 0.998       # multiply epsilon each step

# ---------- 2. SETUP DEVICE (GPU if available) ----------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[my_ai] Using device: {device}")

# ---------- 3. NEURAL NETWORK (YOU WRITE) ----------
class DQN(nn.Module):
    def __init__(self):
        super(DQN, self).__init__()
        # YOUR CODE: define layers (linear, activation, etc.)
        self.Layer_1 = nn.Linear(INPUT_SIZE, 128)
        self.Layer_2 = nn.Linear(128, 128)
        self.Layer_3 = nn.Linear(128, 128)
        self.Layer_4 = nn.Linear(128, ACTION_SIZE)

    def forward(self, x):
        x = F.relu(self.Layer_1(x))
        x = F.relu(self.Layer_2(x))
        x = F.relu(self.Layer_3(x))
        x = self.Layer_4(x)
        return x


# ---------- 4. REPLAY BUFFER (YOU WRITE) ----------
class ReplayBuffer:
    def __init__(self):
        self.buffer = deque(maxlen=REPLAY_CAPACITY)

    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self):
        return random.sample(self.buffer, BATCH_SIZE)
        

    def __len__(self):
        return len(self.buffer)


# ---------- 5. CREATE NETWORKS AND OPTIMIZER ----------
policy_net = DQN().to(device)
target_net = DQN().to(device)
target_net.load_state_dict(policy_net.state_dict())
target_net.eval()

optimizer = torch.optim.Adam(policy_net.parameters(), lr=LEARNING_RATE)
replay_buffer = ReplayBuffer()

epsilon = EPS_START
step_count = 0


# ---------- 6. HELPER FUNCTIONS ----------
def get_state(car, track, max_dist=220):
    # 1. Fire the sensors (updates car.rays_dist)
    car.rays(track.surface)  

    # 2. Convert the list of distances into a GPU tensor
    state_tensor = torch.tensor([car.rays_dist], dtype=torch.float32, device=device)

    # 3. Divide state_tensor by max_dist and return it
    return state_tensor / max_dist


def select_action(state):
    global epsilon
    
    # 1. Roll a decimal between 0 and 1
    if random.random() < epsilon:
        # EXPLORE: return a random action index from 0 to ACTION_SIZE - 1
        return random.randint(0, ACTION_SIZE - 1)
    else:
        # EXPLOIT: pick the action with the highest Q-value
        with torch.no_grad():
            q_values = policy_net(state)
            # Find index of max Q-value and convert tensor to integer
            return torch.argmax(q_values).item()


def compute_reward(car, track, Finished):

    if(car.rays_dist) < 10 or getattr(car, "crashed", False):
        reward -=100
        done = True
        return reward, done
    else:

        reward = 0.1 + (car.speed * 0.1)
        done = False

    if(Finished == True):
        reward += 100


    return reward, done


def optimize_model():

    if len(replay_buffer) < BATCH_SIZE:
        return

    state_b, action_b, reward_b, next_state_b, done_b = replay_buffer.sample(BATCH_SIZE)

    states = torch.cat(state_b).to(device)
    actions = torch.tensor(action_b, dtype=torch.long, device=device).unsqueeze(1)
    rewards = torch.tensor(reward_b, dtype=torch.float32, device=device).unsqueeze(1)
    next_states = torch.cat(next_state_b).to(device)
    dones = torch.tensor(done_b, dtype=torch.float32, device=device).unsqueeze(1)

    current_q = policy_net(states).gather(1, actions)

   
    with torch.no_grad():
        max_next_q = target_net(next_states).max(1)[0].unsqueeze(1)
        # Target formula: reward + gamma * max_next_q * (1 - done)
        target_q = rewards + (GAMMA * max_next_q * (1.0 - dones))

    # 6. Compute Loss (MSE or Huber/SmoothL1)
    loss_fn = nn.MSELoss()
    loss = loss_fn(current_q, target_q)

    # 7. Gradient Descent Step
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()


# ---------- 7. MAIN TRAINING STEP (called every frame from main.py) ----------
def train_step(car, track):
    """Performs one frame of interaction, experience storage, training, and state decay."""
    global step_count, epsilon

    # 1. Sense the current environment state
    state = get_state(car, track)

    # 2. Select an action via epsilon-greedy strategy
    action = select_action(state)

    # 3. Apply action and update car physics/position
    car.apply_action(action)
    car.update()

    # 4. Compute reward and check for crash/terminal condition
    reward, done = compute_reward(car, track)

    # 5. Sense the new state resulting from the action
    next_state = get_state(car, track)

    # 6. Store transition in replay buffer
    replay_buffer.push(state, action, reward, next_state, done)

    # 7. Perform one gradient descent step on a random batch
    optimize_model()

    # 8. Increment global step counter
    step_count += 1

    # 9. Periodically synchronize target network with policy network
    if step_count % TARGET_UPDATE == 0:
        target_net.load_state_dict(policy_net.state_dict())

    # 10. Decay exploration rate epsilon
    epsilon = max(EPS_END, epsilon * EPS_DECAY)

    # 11. Handle episode reset if car crashed or hit terminal state
    if done:
        if hasattr(car, "reset"):
            car.reset(track.start_x, track.start_y)
        else:
            # Fallback attribute resets if car doesn't have a built-in reset() method
            car.x, car.y = track.start_x, track.start_y
            car.angle = 0
            car.speed = 0
            if hasattr(car, "crashed"):
                car.crashed = False