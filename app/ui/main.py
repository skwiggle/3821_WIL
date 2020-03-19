from app.transfer.client import Client
from app.transfer.server import Server, ReadLogFile
import threading

import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Canvas, Rectangle, Color
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label

import time

Window.minimum_width = 500
Window.minimum_height = 500


class mainApp(App):

    title = "Unity Tool (You Guys Decide The Name)"

    def build(self) -> BoxLayout:
        client: Client

        def connect(instance) -> None:
            global client
            try:
                client = Client()
                instance.text = 'Connection Active'
                instance.background_color = [0, 1, 0, 1]
            except:
                instance.text = 'Connection not found'
                instance.background_color = [1, 0, 0, 1]

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

        connect_btn = Button(
            text="Look For Connection (Debugging)",
            on_press=connect,
            background_color=[1, 1, 1, 1])
        update_btn = Button(
            text="Receive (Debugging)")
        debug_layout.add_widget(connect_btn)
        debug_layout.add_widget(update_btn)
        debug_window.add_widget(debug_layout)

        input_layout.add_widget(input)
        input_layout.add_widget(send_btn)
        layout.add_widget(debug_window)
        layout.add_widget(input_layout)
        return layout


if __name__ == '__main__':
    mainApp().run()

