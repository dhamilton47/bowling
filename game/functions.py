"""
    This program defines a BowlingGame class that keeps track of the frames, current frame,
    and score. 
        The roll method adds a roll to the current frame and calculates the score.
        The calculate_score method calculates the score based on the frames.
        The get_next_roll method returns the next roll in the next frame.
        The print_score method prints the score and frames.

    Note that this is a simplified implementation and does not handle all edge cases,
    such as invalid input or incomplete games.

    Created using Llama 3.1 - 405B
"""



class BowlingGame:
    def __init__(self):
        self.frames = []
        self.current_frame = []
        self.score = 0

    def roll(self, pins):
        self.current_frame.append(pins)
        if len(self.current_frame) == 2 or pins == 10:
            self.frames.append(self.current_frame)
            self.current_frame = []
        self.calculate_score()

    def calculate_score(self):
        self.score = 0
        for i, frame in enumerate(self.frames):
            if len(frame) == 1:  # strike
                self.score += 10 + self.get_next_roll(i) + self.get_next_roll(i+1)
            elif len(frame) == 2:  # spare
                self.score += 10 + self.get_next_roll(i)
            else:
                self.score += sum(frame)

    def get_next_roll(self, frame_index):
        if frame_index < len(self.frames) - 1:
            return self.frames[frame_index+1][0]
        elif len(self.current_frame) > 0:
            return self.current_frame[0]
        else:
            return 0

    def print_score(self):
        print("Score:", self.score)
        print("Frames:", self.frames)

# Example usage:
#game = BowlingGame()
#game.roll(5)  # roll 1
#game.roll(3)  # roll 2
#game.roll(10)  # roll 3 (strike)
#game.roll(2)  # roll 4
#game.roll(8)  # roll 5
#game.print_score()