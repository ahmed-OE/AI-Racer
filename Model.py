import torch
import torch.nn as nn
import torch.nn.functional as F
import random
from collections import deque

# ---------- 1. HYPERPARAMETERS (adjust as you like) ----------
INPUT_SIZE = 9
ACTION_SIZE = 13        
GAMMA = 0.99
LEARNING_RATE = 0.001
BATCH_SIZE = 250
REPLAY_CAPACITY = 50000
TARGET_UPDATE = 100     # steps between target network updates
EPS_START = 1.0
EPS_END = 0.01
EPS_DECAY = 0.998       # multiply epsilon each step
GRAD_CLIP_NORM = 10.0   # clip gradients to keep training stable

all_lap_times = [] 

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

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        return zip(*batch)  # transpose to (states, actions, rewards, next_states, dones)


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
    # Assumes car.rays() was already called this frame so rays_dist
    # reflects the car's current position (avoids recomputing 3x/step).
    rays_norm = [d / max_dist for d in car.rays_dist]
 
    speed_norm = car.speed / car.max_speed
    
    angle_norm = car.angle / 180.0
 
    state_list = rays_norm + [speed_norm, angle_norm]
    state_tensor = torch.tensor([state_list], dtype=torch.float32, device=device)
    return state_tensor


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


def compute_reward(car, track):
    crashed = track.is_off_track(car) or min(car.rays_dist) < 10
    total_checkpoints = track.checkpoints[-1][0] if track.checkpoints else 0

    if crashed:
        return -100, True

    reward = 0.1 + (car.speed * 0.1)
    done = False

    # Encourage drifting inside drift-zones
    if car.is_in_drift_zone:
        reward += 1

    if track.is_on_finish_line(car):
        if car.velocity.y > 0.1: 
            print("retared detcted")
            return -150, True
    # ---------------------------------

    reward_car = track.is_on_reward(car)
    if reward_car:
        for number, checkpoint_pos in track.checkpoints:
            if number == car.current_checkpoint:
                distance = reward_car.distance_to(checkpoint_pos)
                if distance < 26:
                    reward += 5
                    car.current_checkpoint += 1
                break

    crossed_finish = (car.left_start and track.is_on_finish_line(car) and car.speed > 0.5)

    if crossed_finish and total_checkpoints < car.current_checkpoint:

        lap_time = car.get_elapsed()
        car.lap_times.append(lap_time)
        all_lap_times.append(lap_time)  
        reward += 100 + (100 - lap_time)

        done = True
        car.finished = True

        if car.velocity.y < 0:
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
       
        target_q = rewards + (GAMMA * max_next_q * (1.0 - dones))

    loss_fn = nn.MSELoss()
    loss = loss_fn(current_q, target_q)


    optimizer.zero_grad()
    loss.backward()

    nn.utils.clip_grad_norm_(policy_net.parameters(), GRAD_CLIP_NORM)
    optimizer.step()



def agent_step(car, track):
    """Handles interaction and memory storage for a single car."""
    car.rays(track.surface)
    state = get_state(car, track)
    action = select_action(state)

    car.apply_action(action)

    car.is_in_drift_zone = track.is_on_drift_zone(car)
    dt = 1 / 60
    car.update_drift_boost(dt)
    car.rays(track.surface)
    
    reward, done = compute_reward(car, track)
    next_state = get_state(car, track)
    
    replay_buffer.push(state, action, reward, next_state, done)
    
    if done:
        car.reset(track.spawn_car_x, track.spawn_car_y)

def group_train_step():
    """Performs one gradient descent step per frame for the whole hive-mind."""
    global step_count, epsilon
    
    optimize_model()
    step_count += 1
    
    if step_count % TARGET_UPDATE == 0:
        target_net.load_state_dict(policy_net.state_dict())
        
    epsilon = max(EPS_END, epsilon * EPS_DECAY)
    

def save_model(filepath="model.pth"):

    torch.save({
        "policy_state_dict": policy_net.state_dict(),
        "target_state_dict": target_net.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "epsilon": epsilon,
        "step_count": step_count,
    }, filepath)
    print(f"Model saved to {filepath} (epsilon={epsilon:.3f}, step={step_count})")

def load_model(filepath="model.pth"):
    global epsilon, step_count
    try:
        checkpoint = torch.load(filepath, map_location=device)

        if isinstance(checkpoint, dict) and "policy_state_dict" in checkpoint:
            policy_net.load_state_dict(checkpoint["policy_state_dict"])
            target_net.load_state_dict(
                checkpoint.get("target_state_dict", checkpoint["policy_state_dict"])
            )
            if "optimizer_state_dict" in checkpoint:
                optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
            epsilon = checkpoint.get("epsilon", epsilon)
            step_count = checkpoint.get("step_count", step_count)
        else:
            
            policy_net.load_state_dict(checkpoint)
            target_net.load_state_dict(policy_net.state_dict())

        print(f"Model loaded from {filepath} (epsilon={epsilon:.3f}, step={step_count})")
    except FileNotFoundError:
        print("No saved model found, starting fresh.")