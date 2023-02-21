# Inspired by PyQt5 Creating Paint Application In 40 Minutes
#  https://www.youtube.com/watch?v=qEgyGyVA1ZQ
import time

# NB If the menus do not work then click on another application and then click back
# and they will work https://python-forum.io/Thread-Tkinter-macOS-Catalina-and-Python-menu-issue

# PyQt documentation links are prefixed with the word 'documentation' in the code below and can be accessed automatically
#  in PyCharm using the following technique https://www.jetbrains.com/help/pycharm/inline-documentation.html

from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog, QDockWidget, QPushButton, QVBoxLayout, \
    QLabel, QMessageBox, QInputDialog, QDialog, QDialogButtonBox, QColorDialog, QToolBar
from PyQt6.QtGui import QIcon, QPainter, QPen, QAction, QPixmap
import sys
import csv, random
import threading
from timerClass import timerClass as timer
from PyQt6.QtCore import Qt, QPoint, QTimer


class PictionaryGame(QMainWindow):  # documentation https://doc.qt.io/qt-6/qwidget.html
    '''
    Painting Application class
    '''

    def __init__(self):
        super().__init__()
        # set window title
        self.setWindowTitle("Pictionary Game - A2 Template")

        # set the windows dimensions
        top = 600
        left = 400
        width = 600
        height = 800
        self.setGeometry(top, left, width, height)

        # set the icon
        # windows version
        self.setWindowIcon(
            QIcon("./icons/paint-brush.png"))  # documentation: https://doc.qt.io/qt-6/qwidget.html#windowIcon-prop
        # mac version - not yet working
        # self.setWindowIcon(QIcon(QPixmap("./icons/paint-brush.png")))

        # player points (default)
        self.playerPoints1 = 0
        self.playerPoints2 = 0
        self.timeLeft = 0
        self.turnPlayer1 = True
        self.playerIName1 = "Player 1"
        self.playerIName2 = "Player 2"
        self.turn = 0
        self.wordFound = 1
        self.hintUsed = False
        self.currentTurn = 0
        self.mode = "easy"

        # image settings (default)
        self.image = QPixmap("./icons/canvas.png")  # documentation: https://doc.qt.io/qt-6/qpixmap.html
        self.image.fill(Qt.GlobalColor.white)  # documentation: https://doc.qt.io/qt-6/qpixmap.html#fill
        mainWidget = QWidget()
        mainWidget.setMaximumWidth(300)

        # draw settings (default)
        self.drawing = False
        self.brushSize = 3
        self.brushColor = Qt.GlobalColor.black  # documentation: https://doc.qt.io/qt-6/qt.html#GlobalColor-enum

        # reference to last point recorded by mouse
        self.lastPoint = QPoint()  # documentation: https://doc.qt.io/qt-6/qpoint.html

        # set up menus
        mainMenu = self.menuBar()  # create a menu bar
        mainMenu.setNativeMenuBar(False)
        mainMenu.setStyleSheet(
            """
                display: flex;
                align-items: center;
                width: 100%; 
                padding:25px;
                text-align: center; 
                font-size: 15px;
                font-family:Lucida Sans;
                background: #9A1663 ;
                color: F49D1A;
               } 
            """
        )
        fileMenu = mainMenu.addMenu(" File")  # add the file menu to the menu bar, the space is required as "File" is reserved in Mac
        brushSizeMenu = mainMenu.addMenu(" Brush Size")  # add the "Brush Size" menu to the menu bar
        brushColorMenu = mainMenu.addMenu(" Brush Color")  # add the "Brush Color" menu to the menu bar
        toolsMenu = mainMenu.addMenu("Tools") #add the "Tools" menu to the menu bar

        # Tools menu actions

        # clear
        clearAction = QAction(QIcon("./icons/clear.png"), "Clear", self)  # create a clear action with a png as an icon
        clearAction.setShortcut("Ctrl+C")  # connect this clear action to a keyboard shortcut
        toolsMenu.addAction(clearAction)  # add this action to the file menu
        clearAction.triggered.connect(self.clear)  # when the menu option is selected or the shortcut is used the clear slot is triggered

        # pick eraser
        eraserAction = QAction(QIcon("./icons/eraser.png"), "Eraser", self)  # create a clear action with a png as an icon
        toolsMenu.addAction(eraserAction)  # add this action to the file menu
        eraserAction.triggered.connect(lambda: self.eraser())

        #Help
        helpAction = QAction(QIcon("./icons/help.png"), "Help", self)  # create a clear action with a png as an icon
        toolsMenu.addAction(helpAction)  # add this action to the file menu
        helpAction.triggered.connect(lambda: self.help())

        # About
        aboutAction = QAction(QIcon("./icons/about.png"), "About", self)  # create a clear action with a png as an icon
        toolsMenu.addAction(aboutAction)  # add this action to the file menu
        aboutAction.triggered.connect(lambda: self.about())

        # file menu items

        # save
        saveAction = QAction(QIcon("./icons/save.png"), "Save", self)  # create a save action with a png as an icon, documentation: https://doc.qt.io/qt-6/qaction.html
        saveAction.setShortcut("Ctrl+S")  # connect this save action to a keyboard shortcut, documentation: https://doc.qt.io/qt-6/qaction.html#shortcut-prop
        fileMenu.addAction(saveAction)  # add the save action to the file menu, documentation: https://doc.qt.io/qt-6/qwidget.html#addAction
        saveAction.triggered.connect(self.save)  # when the menu option is selected or the shortcut is used the save slot is triggered, documentation: https://doc.qt.io/qt-6/qaction.html#triggered

        # exit
        exitAction = QAction(QIcon("./icons/exit.png"), "Exit", self)
        exitAction.setShortcut("Alt+F4")
        fileMenu.addAction(exitAction)
        exitAction.triggered.connect(self.exit)

        # open
        openAction = QAction(QIcon("./icons/open.png"), "Open", self)  # create a clear action with a png as an icon
        fileMenu.addAction(openAction)  # add this action to the file menu
        openAction.triggered.connect(self.open)  # when the menu option is selected or the shortcut is used the clear slot is triggered

        # brush thickness
        threepxAction = QAction(QIcon("./icons/threepx.png"), "3px", self)
        threepxAction.setShortcut("Ctrl+3")
        brushSizeMenu.addAction(threepxAction)  # connect the action to the function below
        threepxAction.triggered.connect(self.threepx)

        fivepxAction = QAction(QIcon("./icons/fivepx.png"), "5px", self)
        fivepxAction.setShortcut("Ctrl+5")
        brushSizeMenu.addAction(fivepxAction)
        fivepxAction.triggered.connect(self.fivepx)

        sevenpxAction = QAction(QIcon("./icons/sevenpx.png"), "7px", self)
        sevenpxAction.setShortcut("Ctrl+7")
        brushSizeMenu.addAction(sevenpxAction)
        sevenpxAction.triggered.connect(self.sevenpx)

        ninepxAction = QAction(QIcon("./icons/ninepx.png"), "9px", self)
        ninepxAction.setShortcut("Ctrl+9")
        brushSizeMenu.addAction(ninepxAction)
        ninepxAction.triggered.connect(self.ninepx)

        # brush colors
        blackAction = QAction(QIcon("./icons/black.png"), "Black", self)
        blackAction.setShortcut("Ctrl+B")
        brushColorMenu.addAction(blackAction)
        blackAction.triggered.connect(self.black)

        redAction = QAction(QIcon("./icons/red.png"), "Red", self)
        redAction.setShortcut("Ctrl+R")
        brushColorMenu.addAction(redAction)
        redAction.triggered.connect(self.red)

        greenAction = QAction(QIcon("./icons/green.png"), "Green", self)
        greenAction.setShortcut("Ctrl+G")
        brushColorMenu.addAction(greenAction)
        greenAction.triggered.connect(self.green)

        yellowAction = QAction(QIcon("./icons/yellow.png"), "Yellow", self)
        yellowAction    .setShortcut("Ctrl+Y")
        brushColorMenu.addAction(yellowAction)
        yellowAction.triggered.connect(self.yellow)

        colorAction = QAction(QIcon("./icons/color.png"), "Custom", self)
        brushColorMenu.addAction(colorAction)
        colorAction.triggered.connect(lambda: self.colorPicker())




        # widget inside the Dock

        # Top dock
        #self.dockTimer = QDockWidget()
        #self.dockTimer = self.addToolBar("Timer dock")

        #widget inside the top dock
        #self.QTimeLeft = QLabel("Time left: " + self.timeLeft)
        #self.QTimeLeft.setStyleSheet("background-color: red")
        #self.dockTimer.addWidget(self.QTimeLeft)

        # Side Dock
        self.dockInfo = QDockWidget()
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dockInfo)
        self.dockInfo.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.dockInfo.setTitleBarWidget(QWidget())

        # Brush dock
        self.toolBrush = QToolBar()
        self.addToolBar(Qt.ToolBarArea.RightToolBarArea, self.toolBrush)
        self.toolBrush.addAction(blackAction)
        self.toolBrush.addAction(redAction)
        self.toolBrush.addAction(greenAction)
        self.toolBrush.addAction(yellowAction)
        self.toolBrush.addAction(colorAction)
        self.toolBrush.addSeparator()
        self.toolBrush.addSeparator()
        self.toolBrush.addAction(threepxAction)
        self.toolBrush.addAction(fivepxAction)
        self.toolBrush.addAction(sevenpxAction)
        self.toolBrush.addAction(ninepxAction)
        self.toolBrush.addSeparator()
        self.toolBrush.addSeparator()
        self.toolBrush.addAction(clearAction)
        self.toolBrush.addAction(eraserAction)
        self.toolBrush.addAction(helpAction)

        #widget inside the side Dock
        playerInfo = QWidget()
        self.vbdock = QVBoxLayout()
        self.playerName1 = QLabel(self.playerIName1)
        self.currentTurn = QLabel("Current turn: ")
        self.playerName2 = QLabel(self.playerIName2)
        self.hintButton = QPushButton("Show hint")
        self.hintButton.clicked.connect(lambda: self.showHint())
        self.guessButton = QPushButton("Word guessed")
        self.guessButton.clicked.connect(lambda: self.guessWord())
        self.skipButton = QPushButton("Skip turn")
        self.skipButton.clicked.connect(lambda: self.skipTurn())
        self.wordButton = QPushButton("Show word")
        self.wordButton.clicked.connect(lambda: self.showWord())
        playerInfo.setLayout(self.vbdock)
        playerInfo.setMaximumSize(200, self.height())
        #add controls to custom widget
        self.vbdock.addWidget(self.currentTurn)
        self.vbdock.addSpacing(20)
        self.vbdock.addWidget(QLabel("Scores:"))
        self.vbdock.addWidget(self.playerName1)
        self.vbdock.addWidget(self.playerName2)
        self.vbdock.addStretch(1)
        self.vbdock.addWidget(self.hintButton)
        self.vbdock.addWidget(self.guessButton)
        self.vbdock.addWidget(self.skipButton)
        self.vbdock.addWidget(self.wordButton)

        #Setting color of dock to purple and changing the button color to beige
        playerInfo.setAutoFillBackground(True)
        playerInfo.setStyleSheet(
            """
                background: #E0144C ;
                color: #EDF5E1;
                } 
                QPushButton{
                    border: 1px solid ;
                    padding: 3px;
                    background: #FFFAD7 ;
                    font-family:Lucida Sans;
                     font-size: 15px;
                    border-radius: 10px;
                    color: black;
                }
            """

        )
        p = playerInfo.palette()
        p.setColor(playerInfo.backgroundRole(), Qt.GlobalColor.gray)
        playerInfo.setPalette(p)

        #set widget for dock
        self.dockInfo.setWidget(playerInfo)

        #Base setup
        self.showFullScreen()
    # event handlers

    # About section
    def about(self):
        msg3 = QMessageBox(parent=self)
        msg3.setWindowTitle("Pictionary")
        msg3.setText("This game was made by Lou-John GENTHON, proud student of Griffith College.\nIf you have any problems you can contact me on: ######@gmail.com")
        msg3.exec()
    # Explains the rules of the game
    def help(self):
        msg3 = QMessageBox(parent=self)
        msg3.setWindowTitle("Pictionary")
        msg3.setText("These are the rules: \n-One player draws\n-One player guesses\n-If the player guesses correctly, he gets 2 points and the player drawing 1 point.\nYou can check the word with the 'Show word' button."
                     "\nIf you guess the word correctly press the 'Word guessed' button.\nIf you're stuck, press the 'Show hint' button, but beware, you will get one less point for guessing."
                     "\nIf you want to skip your turn press the 'Skip turn' button.")
        msg3.exec()

    # Skips the user's turn and doesn't give any points
    def skipTurn(self):
        self.clear()
        msg1 = QMessageBox(parent=self)
        msg1.setWindowTitle("Pictionary")
        if self.wordFound == 1:
            if self.turnPlayer1:
                msg1.setText("You have skipped your turn it is now " + self.playerIName2 + "'s turn to draw")
                self.currentTurn.setText("Current turn: " + self.playerIName2)
                self.currentTurn.update()
                self.turnPlayer1 = False
            else:
                msg1.setText("You have skipped your turn it is now " + self.playerIName1 + "'s turn to draw")
                self.currentTurn.setText("Current turn: " + self.playerIName1)
                self.currentTurn.update()
                self.turnPlayer1 = True
        else:
            if self.turnPlayer1:
                msg1.setText("You are out of time, it is " + self.playerIName2 + "'s turn to draw")
                self.currentTurn.setText("Current turn: " + self.playerIName2)
                self.currentTurn.update()
                self.turnPlayer1 = False
            else:
                msg1.setText("You are out of time, it is " + self.playerIName1 + "'s turn to draw")
                self.currentTurn.setText("Current turn: " + self.playerIName1)
                self.currentTurn.update()
                self.turnPlayer1 = True
        self.turn += 1
        self.wordFound = 1
        self.hintUsed = False
        self.getWord()
        self.currentTurn.update()
        msg1.exec()

    # Pop up to select difficulty
    def selectDiff(self):
        reply = QMessageBox()
        reply.setText("Play on easy mode ?")
        reply.setStandardButtons(QMessageBox.StandardButton.Yes |
                                 QMessageBox.StandardButton.No)
        x = reply.exec()

        if x == QMessageBox.StandardButton.Yes:
            self.getList("easy")
            print("easy")
        else:
            self.getList("hard")
            print("hard")
        self.currentWord = self.getWord()

    # Pops up a message with an int for the current word
    def showHint(self):
        self.hint = self.randomWord[0]
        self.hintUsed = True
        msg3 = QMessageBox(parent=self)
        msg3.setWindowTitle("Pictionary")
        msg3.setText("The first letter of the word is: " + self.hint + "\nAnd the length of the word is: " + str(len(self.randomWord)))
        msg3.exec()

    # Timer class runs a timer run by the thread
    def countdown(self):
        timer.countdown(self)

    # pick a color in the color wheel and assign it to the brush color
    def colorPicker(self):
        color = QColorDialog.getColor()
        self.brushColor = color

    # Increments the players points according to the ruleset and changes the turn
    # The guesser only gets one point if he uses the hint
    # Gives no points if the time has run out
    def guessWord(self):
        self.clear()
        msg1 = QMessageBox(parent=self)
        msg1.setWindowTitle("Pictionary")
        self.turn += 1
        if self.turnPlayer1:
            msg1.setText("Good job! It is now " + self.playerIName2 + "'s turn")
            self.currentTurn.setText("Current turn: " + self.playerIName2)
            self.currentTurn.update()
            self.turnPlayer1 = False
            if self.hintUsed:
                self.playerPoints1 += 1
                self.playerPoints2 += 1
            else:
                self.playerPoints1 += 2
                self.playerPoints2 += 1
            self.playerName1.setText(self.playerIName1 + ": " + str(self.playerPoints1))
            self.playerName2.setText(self.playerIName2 + ": " + str(self.playerPoints2))
            self.playerName1.update()
            self.playerName2.update()
        else:
            msg1.setText("Good job! It is now " + self.playerIName1 + "'s turn")
            self.currentTurn.setText("Current turn: " + self.playerIName1)
            self.currentTurn.update()
            if self.hintUsed:
                self.playerPoints1 += 1
                self.playerPoints2 += 1
            else:
                self.playerPoints1 += 1
                self.playerPoints2 += 2
            self.turnPlayer1 = True
            self.playerName1.setText(self.playerIName1 + ": " + str(self.playerPoints1))
            self.playerName2.setText(self.playerIName2 + ": " + str(self.playerPoints2))
            self.playerName1.update()
            self.playerName2.update()
        self.wordFound = 1
        self.hintUsed = False
        self.getWord()
        msg1.exec()


    # Shows the word the user has to draw
    def showWord(self):
        msg = QMessageBox(text="Press details to see your word", parent=self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Pictionary")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setDetailedText(self.randomWord)
        msg.exec()

    # The user can input player names for better clarity
    def inputPlayerName(self):

        text, ok1 = QInputDialog.getText(self, 'Pictionary', 'Enter player 1 name:')
        if ok1:
            self.playerIName1 = text
            self.playerName1.setText(self.playerIName1 + ": " + str(self.playerPoints1))

        text, ok2 = QInputDialog.getText(self, 'Pictionary', 'Enter player 2 name:')
        if ok2:
            self.playerIName2 = text
            self.playerName2.setText(self.playerIName2 + ": " + str(self.playerPoints2))

    def mousePressEvent(self, event):  # when the mouse is pressed, documentation: https://doc.qt.io/qt-6/qwidget.html#mousePressEvent
        if event.button() == Qt.MouseButton.LeftButton:  # if the pressed button is the left button
            self.drawing = True  # enter drawing mode
            self.lastPoint = event.pos()  # save the location of the mouse press as the lastPoint
            print(self.lastPoint)  # print the lastPoint for debugging purposes

    def mouseMoveEvent(self, event):  # when the mouse is moved, documenation: documentation: https://doc.qt.io/qt-6/qwidget.html#mouseMoveEvent
        if self.drawing:
            painter = QPainter(self.image)  # object which allows drawing to take place on an image
            # allows the selection of brush colour, brish size, line type, cap type, join type. Images available here http://doc.qt.io/qt-6/qpen.html
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawLine(self.lastPoint, event.pos())  # draw a line from the point of the orginal press to the point to where the mouse was dragged to
            self.lastPoint = event.pos()  # set the last point to refer to the point we have just moved to, this helps when drawing the next line segment
            self.update()  # call the update method of the widget which calls the paintEvent of this class

    def mouseReleaseEvent(self, event):  # when the mouse is released, documentation: https://doc.qt.io/qt-6/qwidget.html#mouseReleaseEvent
        if event.button() == Qt.MouseButton.LeftButton:  # if the released button is the left button, documentation: https://doc.qt.io/qt-6/qt.html#MouseButton-enum ,
            self.drawing = False  # exit drawing mode

    # paint events
    def paintEvent(self, event):
        # you should only create and use the QPainter object in this method, it should be a local variable
        canvasPainter = QPainter(self)  # create a new QPainter object, documentation: https://doc.qt.io/qt-6/qpainter.html
        canvasPainter.drawPixmap(QPoint(), self.image)  # draw the image , documentation: https://doc.qt.io/qt-6/qpainter.html#drawImage-1

    # resize event - this function is called
    def resizeEvent(self, event):
        self.image = self.image.scaled(self.width(), self.height())

    # slots
    def save(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                                                  "PNG(*.png);;JPG(*.jpg *.jpeg);;All Files (*.*)")
        if filePath == "":  # if the file path is empty
            return  # do nothing and return
        self.image.save(filePath)  # save file image to the file path

    def clear(self):
        self.image.fill(
            Qt.GlobalColor.white)  # fill the image with white, documentation: https://doc.qt.io/qt-6/qimage.html#fill-2
        self.update()  # call the update method of the widget which calls the paintEvent of this class

    def threepx(self):  # the brush size is set to 3
        self.brushSize = 3

    def fivepx(self):
        self.brushSize = 5

    def sevenpx(self):
        self.brushSize = 7

    def ninepx(self):
        self.brushSize = 9

    def black(self):  # the brush color is set to black
        self.brushColor = Qt.GlobalColor.black

    def black(self):
        self.brushColor = Qt.GlobalColor.black

    def red(self):
        self.brushColor = Qt.GlobalColor.red

    def green(self):
        self.brushColor = Qt.GlobalColor.green

    def yellow(self):
        self.brushColor = Qt.GlobalColor.yellow

    def eraser(self):
        self.brushColor = Qt.GlobalColor.white

    #Get a random word from the list read from file
    def getWord(self):
        self.randomWord = random.choice(self.wordList)
        print(self.randomWord)
        return self.randomWord

    #read word list from file
    def getList(self, mode):
        with open(mode + 'mode.txt') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                #print(row)
                self.wordList = row
                line_count += 1
            #print(f'Processed {line_count} lines.')

    def exit(self):
        self.exit()

    # open a file
    def open(self):
        '''
        This is an additional function which is not part of the tutorial. It will allow you to:
         - open a file dialog box,
         - filter the list of files according to file extension
         - set the QImage of your application (self.image) to a scaled version of the file)
         - update the widget
        '''
        filePath, _ = QFileDialog.getOpenFileName(self, "Open Image", "",
                                                  "PNG(*.png);;JPG(*.jpg *.jpeg);;All Files (*.*)")
        if filePath == "":  # if not file is selected exit
            return
        with open(filePath, 'rb') as f:  # open the file in binary mode for reading
            content = f.read()  # read the file
        self.image.loadFromData(content)  # load the data into the file
        width = self.width()  # get the width of the current QImage in your application
        height = self.height()  # get the height of the current QImage in your application
        self.image = self.image.scaled(width, height)  # scale the image from file and put it in your QImage
        self.update()  # call the update method of the widget which calls the paintEvent of this class


# this code will be executed if it is the main module but not if the module is imported
#  https://stackoverflow.com/questions/419163/what-does-if-name-main-do
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(
        """
                QPushButton{
                    border: 1px solid ;
                    padding: 3px;
                    background: #FFFAD7 ;
                    font-family:Lucida Sans;
                     font-size: 15px;
                    border-radius: 10px;
                    color: black;
                }


                QLabel{
                    font-family:Lucida Sans;
                    font-size: 15px;
                    font-weight: Medium;
                    color: black;
                }

            """
    )
    window = PictionaryGame()
    window.show()
    # Start the difficulty selection thread
    modeChoice_thread = threading.Thread(target=window.selectDiff())
    modeChoice_thread.start()
    # Start the name input thread as soon as the difficulty has been chosen
    inputName_thread = threading.Thread(target=window.inputPlayerName())
    inputName_thread.start()
    # Start the countdown thread as soon as the user has inputed the names
    #countdown_thread = threading.Thread(target=window.countdown)
    #countdown_thread.start()
    app.exec()  # start the event loop running
