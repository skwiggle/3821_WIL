import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Canvas, Rectangle, Color
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label

Window.minimum_width = 500
Window.minimum_height = 500

class mainApp(App):

    title = "Unity Tool (You Guys Decide The Name)"

    def build(self):
        layout = BoxLayout(
            orientation='vertical',
            spacing=0, padding=20)
        debug_window = ScrollView(
            size_hint=(1, 0.8))
        debug_layout = BoxLayout(
            orientation='vertical',
            padding=10)
        input_layout = BoxLayout(
            orientation='horizontal',
            spacing=0,
            size_hint=(1, 0.2))

        input = TextInput(
            size_hint=(0.8, 1))
        input.show_keyboard()

        send_btn = Button(
            font_size=10,
            size_hint=(0.2, 1),
            text='SEND')


        for n in range(50):
            placeholder = Label(
                text="Placeholder line %i" % n,
                halign='left')
            debug_layout.add_widget(placeholder)
        debug_window.add_widget(debug_layout)

        input_layout.add_widget(input)
        input_layout.add_widget(send_btn)
        layout.add_widget(debug_window)
        layout.add_widget(input_layout)
        return layout


if __name__ == '__main__':
    mainApp().run()