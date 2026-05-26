# main.py
import kivy
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
import os

from regression_core_android import calculate_single_trip

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        self.input_w = TextInput(hint_text="Вес (тонн)", multiline=False)
        self.input_s = TextInput(hint_text="Скорость (км/ч)", multiline=False)
        self.input_f = TextInput(hint_text="Расход (литров)", multiline=False)
        
        btn_calc = Button(text="Рассчитать", on_press=self.run_calc)
        self.result_label = Label(text="Введите данные и нажмите кнопку")
        btn_export = Button(text="Экспорт отчета в .txt", on_press=self.save_report)
        
        layout.add_widget(self.input_w)
        layout.add_widget(self.input_s)
        layout.add_widget(self.input_f)
        layout.add_widget(btn_calc)
        layout.add_widget(self.result_label)
        layout.add_widget(btn_export)
        
        self.add_widget(layout)
        self.last_report = ""

    def run_calc(self, instance):
        try:
            w, s, f = float(self.input_w.text), float(self.input_s.text), float(self.input_f.text)
            res = calculate_single_trip(w, s, f)
            
            self.last_report = (f"ОТЧЕТ О ПОЕЗДКЕ:\n"
                                f"Норма: {res['predicted']:.2f} л.\n"
                                f"Граница: {res['upper_bound']:.2f} л.\n"
                                f"Перерасход: {res['extra_fuel']:.2f} л.\n"
                                f"Эко-ущерб: {res['damage']:.2f} руб.")
            self.result_label.text = self.last_report
        except ValueError:
            self.result_label.text = "Ошибка: введите корректные числа!"

    def save_report(self, instance):
        if not self.last_report:
            return
        # Сохранение во внутреннюю память приложения
        file_path = os.path.join(App.get_running_app().user_data_dir, "report.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.last_report)
        Popup(title="Экспорт", content=Label(text=f"Сохранено в:\n{file_path}"), size_hint=(0.8, 0.4)).open()

class FuelApp(App):
    def build(self):
        return MainScreen()

if __name__ == '__main__':
    FuelApp().run()