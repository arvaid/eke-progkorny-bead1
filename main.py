from kivy.app import App
from kivy.uix.widget import Widget


class Menu(Widget):
    pass


class SudokuApp(App):
    def build(self):
        return Menu()


if __name__ == '__main__':
    SudokuApp().run()
