import kivy
from kivy.app import App
from kivy.uix.button import Button

class mainApp(App):
    def build(self):
        return Label(text="Template")


if __name__ == '__main__':
    mainApp().run()