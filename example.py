from arkania import SimpleEnv
import time


def human_interface():
    """
        For a human user interface we could do:
          W = move north
          A = move west
          S = move south
          D = move east
          E = pick up
          X = put down
          C = consume
          R = rest
          Up-Arrow = throw north
          Left-Arrow = throw west
          Down-Arrow = throw south
          Right-Arrow throw east
    """
    import keyboard
    env = SimpleEnv()
    env.reset()
    env.render()

    # Turn this off before committing
    debugging = False

    done = False
    while not done:
        env.render()
        time.sleep(0.15)

        action = 0
        ch = keyboard.read_key()
        print(f"getch -> ({ch})")

        if ch == 'esc': break
        if ch == 'w': action = 1
        if ch == 'd': action = 2
        if ch == 's': action = 3
        if ch == 'a': action = 4
        if ch == 'e': action = 5
        if ch == 'x': action = 6
        if ch == 'c': action = 7
        if ch == 'up': action = 8
        if ch == 'right': action = 9
        if ch == 'down': action = 10
        if ch == 'left': action = 11

        state, reward, done, debug_info = env.step(action)

        if debugging:
            print(f"agent: ({env.agent.x}, {env.agent.y})")
            print(state['sight'])

    env.viewer.close()


if __name__ == "__main__":
    human_interface()
