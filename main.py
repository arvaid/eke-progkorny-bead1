from kivy.app import App
from kivy.config import Config
from kivy.uix.screenmanager import Screen
from kivy.uix.screenmanager import ScreenManager


sm = ScreenManager()


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


class RulesScreen(Screen):
    def __init__(self, **kwargs):
        super(RulesScreen, self).__init__(**kwargs)

    @staticmethod
    def back():
        sm.current = 'Menu'


class ScoreboardScreen(Screen):
    def __init__(self, **kwargs):
        super(ScoreboardScreen, self).__init__(**kwargs)


class SudokuApp(App):
    def build(self):
        Config.set('graphics', 'resizable', False)

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
