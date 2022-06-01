from game import *
from config import device
from model_basic_conv2d import DQNBasicConv2d
from memory import *
import math
import torch
from torch import optim as optim
from torch import nn as nn
from itertools import count
import os

BATCH_SIZE = 2048
GAMMA = 0.999
EPS_START = 0.9
EPS_END = 0.05
EPS_DECAY = 10000
TARGET_UPDATE = 10
SAVE_INTERVAL = 100

POSSIBLE_ACTIONS = 4 * GAME_COLS

policy_net = DQNBasicConv2d(GAME_ROWS, GAME_COLS, POSSIBLE_ACTIONS).to(device)
target_net = DQNBasicConv2d(GAME_ROWS, GAME_COLS, POSSIBLE_ACTIONS).to(device)
target_net.load_state_dict(policy_net.state_dict())
target_net.eval()

optimizer = optim.RMSprop(policy_net.parameters())
memory = ReplayMemory(10000)

selections_done = 0


def select_action(state):
    global selections_done

    eps_threshold = EPS_END + (EPS_START - EPS_END) * math.exp(-1. * selections_done / EPS_DECAY)
    selections_done += 1
    if random.random() > eps_threshold:
        with torch.no_grad():
            return policy_net(state).max(1)[1].view(1, 1)
    else:
        return torch.tensor([[random.randrange(GAME_ACTIONS)]], device=device, dtype=torch.int)


def optimize_model():
    if len(memory) < BATCH_SIZE:
        return
    transitions = memory.sample(BATCH_SIZE)

    batch = Transition(*zip(*transitions))

    non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                            batch.next_state)), device=device, dtype=torch.bool)
    non_final_next_states = torch.cat([s for s in batch.next_state
                                       if s is not None])
    state_batch = torch.cat(batch.state)
    action_batch = torch.cat(batch.action)
    reward_batch = torch.cat(batch.reward)

    state_action_values = policy_net(state_batch).gather(1, action_batch)

    next_state_values = torch.zeros(BATCH_SIZE, device=device)
    next_state_values[non_final_mask] = target_net(non_final_next_states).max(1)[0].detach()

    expected_state_action_values = (next_state_values * GAMMA) + reward_batch

    criterion = nn.SmoothL1Loss()
    loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))

    optimizer.zero_grad()
    loss.backward()
    for param in policy_net.parameters():
        param.grad.data.clamp_(-1, 1)
    optimizer.step()


def get_input(state: GameState):
    data = state.data[[GameState.DATA_INDEX_FROZEN_BLOCKS, GameState.DATA_INDEX_FALLING_BLOCKS]]
    data = torch.tensor(data, dtype=torch.float).unsqueeze(0)
    return data


def get_reward(state: GameState):
    reward = state.op_hard_drop
    reward += state.single_line_cleared * 100
    reward += state.double_lines_cleared * 200
    reward += state.triple_lines_cleared * 400
    reward += state.tetris_line_cleared * 800
    return reward


def perform_action(state: GameState, action_code):
    rotation_times = action_code // GAME_COLS
    while rotation_times > 0:
        user_rotate_piece(state)
        rotation_times -= 1

    horizontal_location = action_code % GAME_COLS
    horizontal_distance = horizontal_location - state.falling_piece_location[1]
    horizontal_distance -= 1
    while horizontal_distance < 0:
        horizontal_distance += 1
        user_move_piece_left(state)
    while horizontal_distance > 0:
        horizontal_distance -= 1
        user_move_piece_right(state)

    user_drop_piece(state)
    return state


def _test_perform_action():
    print("_test_perform_action")

    state = new_game()
    for piece in PIECES:
        state.falling_piece = piece
        update_falling_blocks(state)
        print(state.blocks[:4])

        for i in range(POSSIBLE_ACTIONS):
            s = copy.deepcopy(state)
            perform_action(s, i)
            print(i, s.blocks[15:])


def train():
    model_weight_filepath = "weights/{}.II.pth".format(type(target_net).__name__)

    if os.path.exists(model_weight_filepath):
        policy_net.load_state_dict(torch.load(model_weight_filepath))
        target_net.load_state_dict(policy_net.state_dict())
        target_net.eval()

    episode_count = 5000
    episode_durations = []
    episode_scores = []

    for episode in range(episode_count):
        game_state = new_game()
        for actions_done in count():
            model_state = get_input(game_state)
            initial_score = game_state.score

            action_code = select_action(model_state)
            perform_action(game_state, action_code)
            step(game_state)

            reward = game_state.score - initial_score
            reward = torch.tensor([reward], device=device)

            game_over = game_state.status != GameStatus.RUNNING

            next_model_state = get_input(game_state)
            if game_over:
                next_model_state = None

            memory.push(model_state, action_code, next_model_state, reward)

            optimize_model()
            if game_over or actions_done > 1000:
                episode_durations.append(actions_done + 1)
                episode_scores.append(game_state.score)
                break

        if episode % TARGET_UPDATE == 0:
            print('==== episode {} ===='.format(episode))
            print(
                'selections_done', selections_done,
                'max_score', np.max(episode_scores),
                'mean_score', np.mean(episode_scores[-10:]),
                'mean_duration', np.mean(episode_durations[-10:]),
                sep='\t'
            )
            print(game_state)
            print(game_state.blocks)
            target_net.load_state_dict(policy_net.state_dict())

        if episode % SAVE_INTERVAL == 0:
            torch.save(target_net.state_dict(), model_weight_filepath)

    print('completing...')
    print('durations', episode_durations)
    torch.save(target_net.state_dict(), model_weight_filepath)


if __name__ == "__main__":
    train()
