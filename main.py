from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen, ScreenManager, WipeTransition

from datetime import datetime
import sqlite3
import os

Config.set('graphics', 'resizable', False)
sm = ScreenManager()

cell_color_default = (0, 0, 0, 1)

cell_background_default = (1, 1, 1, 1)
cell_background_accent = (0.93, 0.93, 0.93, 1)
cell_background_selected = (1, 0.8, 0.8, 1)
cell_background_generated = (0.83, 0.83, 0.83, 1)

db_uri = 'scores.db'


# másodpercek megjelenítése mm:ss formátumban
def seconds2str(seconds: int) -> str:
    return str(seconds // 60).zfill(2) + ':' + str(seconds % 60).zfill(2)


def open_db():
    if os.path.isfile(db_uri):
        try:
            conn = sqlite3.connect(db_uri)
        except sqlite3.Error:
            print('Adatbázis hiba!')
            return False
        cur = conn.cursor()

        cmd = 'CREATE TABLE IF NOT EXISTS scores(date DATETIME PRIMARY KEY, name VARCHAR(20), seconds INTEGER)'
        cur.execute(cmd)

        return [conn, cur]
    return False


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)

    @staticmethod
    def new_game():
        sm.current = 'Game'

    @staticmethod
    def rules():
        sm.current = 'Rules'

    @staticmethod
    def scoreboard():
        sm.current = 'Scoreboard'

    @staticmethod
    def exit_game():
        App.get_running_app().stop()


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self._keyboard = None
        self.game_started = False
        self.seconds = 0
        self.board = []
        self.cells = []
        self.selection = None
        self.clockEvent = None

    def build(self):
        self.new_game()

    def _on_enter(self):
        self.new_game()
        self._keyboard = Window.request_keyboard(self._keyboard_closed(), self)
        self._keyboard.bind(on_key_down=self._keyboard_press)

    def _on_leave(self):
        self._keyboard_closed()

    def _clock_callback(self, dt):
        self.seconds += 1
        self.timer.text = seconds2str(self.seconds)

    def _keyboard_closed(self):
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self._keyboard_press)
            self._keyboard = None

    def _keyboard_press(self, keyboard, keycode, text, modifiers):
        if self.selection:
            if keycode[1] == '1' or keycode[1] == 'numpad1':
                self.board[self.selection[0]][self.selection[1]] = 1
            elif keycode[1] == '2' or keycode[1] == 'numpad2':
                self.board[self.selection[0]][self.selection[1]] = 2
            elif keycode[1] == '3' or keycode[1] == 'numpad3':
                self.board[self.selection[0]][self.selection[1]] = 3
            elif keycode[1] == '4' or keycode[1] == 'numpad4':
                self.board[self.selection[0]][self.selection[1]] = 4
            elif keycode[1] == '5' or keycode[1] == 'numpad5':
                self.board[self.selection[0]][self.selection[1]] = 5
            elif keycode[1] == '6' or keycode[1] == 'numpad6':
                self.board[self.selection[0]][self.selection[1]] = 6
            elif keycode[1] == '7' or keycode[1] == 'numpad7':
                self.board[self.selection[0]][self.selection[1]] = 7
            elif keycode[1] == '8' or keycode[1] == 'numpad8':
                self.board[self.selection[0]][self.selection[1]] = 8
            elif keycode[1] == '9' or keycode[1] == 'numpad9':
                self.board[self.selection[0]][self.selection[1]] = 9
            elif keycode[1] == 'delete' or keycode[1] == 'backspace':
                self.board[self.selection[0]][self.selection[1]] = 0
            elif keycode[1] == 'left':
                row = self.selection[0]
                if self.selection[1] > 0:
                    for col in range(self.selection[1] - 1, -1, -1):
                        if self.cells[row][col].select():
                            break
            elif keycode[1] == 'right':
                row = self.selection[0]
                if self.selection[1] < 9:
                    for col in range(self.selection[1] + 1, 9):
                        if self.cells[row][col].select():
                            break
            elif keycode[1] == 'up':
                col = self.selection[1]
                if self.selection[0] > 0:
                    for row in range(self.selection[0] - 1, -1, -1):
                        if self.cells[row][col].select():
                            break
            elif keycode[1] == 'down':
                col = self.selection[1]
                if self.selection[0] < 9:
                    for row in range(self.selection[0] + 1, 9):
                        if self.cells[row][col].select():
                            break
            self.update_grid()
            if self.check_board():
                self.win()

    def start_timer(self):
        if self.clockEvent:
            self.clockEvent.cancel()
        self.clockEvent = Clock.schedule_interval(self._clock_callback, 1)

    def init_board(self):
        self.board.clear()
        for i in range(9):
            self.board.append([0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.generate_puzzle()

    def new_game(self):
        self.init_board()
        self.create_cells()
        self.seconds = 0
        self.timer.text = seconds2str(self.seconds)
        self.start_timer()
        self.game_started = True

    def generate_puzzle(self):
        base = 3
        side = base * base

        # pattern for a baseline valid solution
        def pattern(r, c):
            return (base * (r % base) + r // base + c) % side

        # randomize rows, columns and numbers (of valid base pattern)
        from random import sample

        def shuffle(s):
            return sample(s, len(s))

        r_base = range(base)
        rows = [g * base + r for g in shuffle(r_base) for r in shuffle(r_base)]
        cols = [g * base + c for g in shuffle(r_base) for c in shuffle(r_base)]
        nums = shuffle(range(1, base * base + 1))

        # produce board using randomized baseline pattern
        self.board = [[nums[pattern(r, c)] for c in cols] for r in rows]

        squares = side * side
        empties = squares * 3 // 4
        for p in sample(range(squares), empties):
            # noinspection PyTypeChecker
            self.board[p // side][p % side] = 0

    def solve(self):
        def find_next_empty(i, j):
            for row in range(i, 9):
                for col in range(j, 9):
                    if self.board[row][col] == 0:
                        return row, col
            for row in range(0, 9):
                for col in range(0, 9):
                    if self.board[row][col] == 0:
                        return row, col
            return -1, -1

        def is_valid(i, j, e):
            row_ok = all([e != self.board[i][x] for x in range(9)])
            if row_ok:
                col_ok = all([e != self.board[x][j] for x in range(9)])
                if col_ok:
                    # finding the top left x,y co-ordinates of the section containing the i,j cell
                    sec_top_x, sec_top_y = 3 * (i // 3), 3 * (j // 3)  # floored quotient should be used here.
                    for x in range(sec_top_x, sec_top_x + 3):
                        for y in range(sec_top_y, sec_top_y + 3):
                            if self.board[x][y] == e:
                                return False
                    return True
                return False

        def solve_sudoku(i=0, j=0):
            i, j = find_next_empty(i, j)
            if i == -1:
                return True
            for e in range(1, 10):
                if is_valid(i, j, e):
                    self.board[i][j] = e
                    self.cells[i][j].text = str(e)
                    if solve_sudoku(i, j):
                        return True
                    # Undo the current cell for backtracking
                    self.board[i][j] = 0
            return False

        return solve_sudoku()

    def clear_board(self):
        for cell in self.grid.children:
            row = cell.row
            col = cell.col
            if not cell.generated:
                cell.text = ''
                self.board[row][col] = 0

    def reset(self):
        self.clear_board()
        self.seconds = 0
        self.timer.text = seconds2str(self.seconds)
        self.start_timer()

    def update_grid(self):
        for cell in self.grid.children:
            value = self.board[cell.row][cell.col]
            if value != 0:
                cell.text = str(value)
            else:
                cell.text = ''

    def cheat(self):
        if self.game_started:
            self.clear_board()
            self.clockEvent.cancel()
            success = self.solve()
            self.update_grid()
            if success:
                self.win()

    def check_board(self):
        for row in range(9):
            row_nums = set()
            for col in range(9):
                num = self.board[row][col]
                # van-e üres mező
                if num == 0:
                    return False
                # van-e ismétlődés a sorban
                if num in row_nums:
                    return False
                row_nums.add(num)

        for col in range(9):
            col_nums = set()
            for row in range(9):
                num = self.board[row][col]
                # van-e ismétlődés az oszlopban
                if num in col_nums:
                    return False
                col_nums.add(num)

        for square in range(1, 4):
            square_nums = set()
            for row in range(1, 4):
                for col in range(1, 4):
                    num = self.board[square * row][square * col]
                    # van-e ismétlődés a 3x3-as négyzetben
                    if num in square_nums:
                        return False
                    square_nums.add(num)
        return True

    def win(self):
        self.game_started = False
        scoreboard = False

        conn, cur = open_db()
        count = cur.execute('SELECT count(*) FROM scores').fetchone()[0]

        if count < 10:
            scoreboard = True
        else:
            for row in cur.execute('SELECT date, name, seconds FROM scores ORDER BY seconds LIMIT 10'):
                if self.seconds < row[2]:
                    scoreboard = True
                    break
        conn.close()

        if scoreboard:
            popup = EnterNamePopup(self.seconds)
            popup.open()

    def create_cells(self):
        self.grid.clear_widgets()
        self.cells.clear()
        for row in range(9):
            self.cells.append([])
            for col in range(9):
                cell = SudokuCell(row, col, self)
                if self.board[row][col] != 0:
                    cell.text = str(self.board[row][col])
                    cell.generated = True
                else:
                    cell.generated = False

                cell.set_background()
                self.grid.add_widget(cell)
                self.cells[row].append(cell)
        for cell in self.grid.children:
            value = self.board[cell.row][cell.col]
            if value != 0:
                cell.text = str(value)
                cell.generated = True
            else:
                cell.text = ''
                cell.generated = False
            cell.set_background()

    def select(self, row, col):
        for cell in self.grid.children:
            if isinstance(cell, SudokuCell):
                cell.set_background()
        self.selection = (row, col)

    @staticmethod
    def back():
        sm.current = 'Menu'


class SudokuCell(Button):
    def __init__(self, row, col, screen, generated=False, **kwargs):
        super(SudokuCell, self).__init__(**kwargs)
        self.row = row
        self.col = col
        self.screen = screen
        self.generated = generated
        self.background_normal = "white.png"
        self.background_down = "white.png"
        self.color = cell_color_default
        self.set_background()

    def set_background(self):
        if self.generated:
            self.background_color = cell_background_generated
        else:
            upper_left = (self.row < 3 and self.col < 3)
            upper_right = (self.row < 3 and self.col > 5)
            middle = (3 <= self.row <= 5 and 3 <= self.col <= 5)
            lower_left = (self.row > 5 and self.col < 3)
            lower_right = (self.row > 5 and self.col > 5)
            if upper_left or upper_right or middle or lower_left or lower_right:
                self.background_color = cell_background_accent
            else:
                self.background_color = cell_background_default

    def select(self):
        if self.generated:
            return False
        self.screen.select(self.row, self.col)
        self.background_color = cell_background_selected
        return True


class RulesScreen(Screen):
    def __init__(self, **kwargs):
        super(RulesScreen, self).__init__(**kwargs)

    @staticmethod
    def back():
        sm.current = 'Menu'


class ScoreboardScreen(Screen):
    def __init__(self, **kwargs):
        super(ScoreboardScreen, self).__init__(**kwargs)

    def create_list(self):
        self.scoreList.clear_widgets()
        conn, cur = open_db()

        count = 0
        for row in cur.execute('SELECT date, name, seconds FROM scores ORDER BY seconds LIMIT 10'):
            count += 1
            row_layout = BoxLayout()

            label1 = Label(text=f'{count}.')
            label1.color = (0, 0, 0, 1)
            label1.font_size = 20
            row_layout.add_widget(label1)

            label2 = Label(text=str(row[1]))
            label2.color = (0, 0, 0, 1)
            label2.font_size = 20
            row_layout.add_widget(label2)

            label3 = Label(text=seconds2str(row[2]))
            label3.color = (0, 0, 0, 1)
            label3.font_size = 20
            row_layout.add_widget(label3)

            label4 = Label(text=str(row[0]).split('.')[0])
            label4.color = (0, 0, 0, 1)
            label4.font_size = 20
            row_layout.add_widget(label4)

            self.scoreList.add_widget(row_layout)

        conn.close()

    @staticmethod
    def back():
        sm.current = 'Menu'


class EnterNamePopup(Popup):
    def __init__(self, seconds, **kwargs):
        super(EnterNamePopup, self).__init__(**kwargs)
        self.title = 'Felkerültél a pontlistára!'
        self.auto_dismiss = False
        self.seconds = seconds

    def save_score(self):
        conn, cur = open_db()

        if self.player_name.text:
            name = self.player_name.text
        else:
            name = '-'

        record = (datetime.now(), name, self.seconds)
        cur.execute('INSERT INTO  scores VALUES (?, ?, ?)', record)
        conn.commit()
        conn.close()
        self.dismiss()


class SudokuApp(App):
    def __init__(self, **kwargs):
        super(SudokuApp, self).__init__(**kwargs)

    def build(self):
        sm.transition = WipeTransition()

        menu_screen = MenuScreen(name='Menu')
        sm.add_widget(menu_screen)

        game_screen = GameScreen(name='Game')
        sm.add_widget(game_screen)

        rules_screen = RulesScreen(name='Rules')
        sm.add_widget(rules_screen)

        scoreboard_screen = ScoreboardScreen(name='Scoreboard')
        sm.add_widget(scoreboard_screen)

        sm.current = 'Menu'
        return sm


if __name__ == '__main__':
    SudokuApp().run()
