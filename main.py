from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager, WipeTransition

Config.set('graphics', 'resizable', False)
sm = ScreenManager()

cell_color_default = (0, 0, 0, 1)

cell_background_default = (1, 1, 1, 1)
cell_background_selected = (1, 0.8, 0.8, 1)
cell_background_generated = (0.93, 0.93, 0.93, 1)


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
        self.board = []
        self.selection = None
        self.new_game()

    def new_game(self):
        self.board.clear()
        for i in range(9):
            self.board.append([0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.generate_puzzle()
        for cell in self.grid.children:
            value = self.board[cell.row][cell.col]
            if value != 0:
                cell.text = str(value)
                cell.generated = True
                cell.color = cell_color_default
                cell.background_color = cell_background_generated
            else:
                cell.text = ''
                cell.generated = False
                cell.color = cell_color_default
                cell.background_color = cell_background_default

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

    def reset(self):
        for cell in self.grid.children:
            row = cell.row
            col = cell.col
            if not cell.generated:
                cell.text = ''
                self.board[row][col] = 0

    def update_grid(self):
        for cell in self.grid.children:
            value = self.board[cell.row][cell.col]
            if value != 0:
                cell.text = str(value)
            else:
                cell.text = ''

    def create_cells(self):
        self.new_game()
        self.grid.clear_widgets()
        for row in range(9):
            for col in range(9):
                cell = SudokuCell(row, col, self)
                if self.board[row][col] != 0:
                    cell.text = str(self.board[row][col])
                    cell.generated = True
                    cell.color = cell_color_default
                    cell.background_color = cell_background_generated
                else:
                    cell.generated = False
                    cell.color = cell_color_default
                    cell.background_color = cell_background_default
                cell.background_normal = "white.png"
                cell.background_down = "white.png"
                self.grid.add_widget(cell)

    def select(self, row, col):
        for cell in self.grid.children:
            if not cell.generated:
                cell.background_color = cell_background_default
        self.selection = (row, col)

    def input(self, keycode):
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
            self.update_grid()

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

    def select(self):
        if not self.generated:
            self.screen.select(self.row, self.col)
            self.background_color = cell_background_selected


class RulesScreen(Screen):
    def __init__(self, **kwargs):
        super(RulesScreen, self).__init__(**kwargs)

    @staticmethod
    def back():
        sm.current = 'Menu'


class ScoreboardScreen(Screen):
    def __init__(self, **kwargs):
        super(ScoreboardScreen, self).__init__(**kwargs)

    @staticmethod
    def back():
        sm.current = 'Menu'


class SudokuApp(App):
    def __init__(self, **kwargs):
        super(SudokuApp, self).__init__(**kwargs)
        self.__keyboard = Window.request_keyboard(self.press, self)
        self.__keyboard.bind(on_key_down=self.press)

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

    @staticmethod
    def press(keyboard, keycode, text, modifiers):
        if sm.current == 'Game':
            game_screen = sm.children[0]
            game_screen.input(keycode)


if __name__ == '__main__':
    SudokuApp().run()
