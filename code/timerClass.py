import time

class timerClass:
    def __init__(self, timeLeft, wordFound):
        self.timeLeft = timeLeft
        self.wordFound = wordFound

    def getTime(self):
        return self.timeLeft

    def setTime(self):
        self.timeLeft = 10

    def setWordFound(self):
        self.wordFound = 1

    def countdown(self):
        self.timeLeft = 10
        for x in range(10):
            self.timeLeft -= 1
            time.sleep(1)
            print(self.timeLeft)
            self.QTimeLeft.setText("Time left: " + str(self.timeLeft))
            self.QTimeLeft.update()
        print("Out of time")
        self.wordFound = 0