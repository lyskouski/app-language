from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup


def show_delete_confirmation(on_confirm):
    app = App.get_running_app()
    message = Label(
        text=app._('delete_confirmation_message', app.locale),
        halign='left',
        valign='middle',
    )
    message.bind(size=lambda instance, size: setattr(instance, 'text_size', size))

    buttons = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
    cancel_button = Button(text=app._('button_cancel', app.locale))
    delete_button = Button(text=app._('button_delete', app.locale))
    buttons.add_widget(cancel_button)
    buttons.add_widget(delete_button)

    content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(16))
    content.add_widget(message)
    content.add_widget(buttons)

    popup = Popup(
        title=app._('delete_confirmation_title', app.locale),
        content=content,
        size_hint=(0.85, None),
        height=dp(190),
    )
    cancel_button.bind(on_release=lambda *_: popup.dismiss())

    def confirm(_button):
        popup.dismiss()
        on_confirm()

    delete_button.bind(on_release=confirm)
    popup.open()
    return popup