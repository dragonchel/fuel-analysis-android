# main.py
import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView

from regression_core_android import calculate_single_trip, train_model_from_excel, load_model, export_to_pdf_android

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=15)
        
        layout.add_widget(Label(text="ВХОД В СИСТЕМУ АНАЛИТИКИ", font_size='20sp', bold=True))
        
        self.login_input = TextInput(hint_text="Логин", multiline=False, write_tab=False)
        self.pass_input = TextInput(hint_text="Пароль", password=True, multiline=False, write_tab=False)
        
        layout.add_widget(self.login_input)
        layout.add_widget(self.pass_input)
        
        btn_login = Button(text="Войти", size_hint_y=None, height='50dp', background_color=(0.2, 0.6, 0.2, 1))
        btn_login.bind(on_press=self.verify_login)
        layout.add_widget(btn_login)
        
        self.error_label = Label(text="", color=(1, 0, 0, 1))
        layout.add_widget(self.error_label)
        
        self.add_widget(layout)

    def verify_login(self, instance):
        login = self.login_input.text.strip()
        password = self.pass_input.text.strip()
        
        if login == "admin" and password == "admin123":
            self.error_label.text = ""
            self.manager.current = 'admin_main'
        elif login == "dispatcher" and password == "disp123":
            self.error_label.text = ""
            self.manager.current = 'dispatcher_main'
        else:
            self.error_label.text = "Неверный логин или пароль!"

class AdminMainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        self.status_label = Label(text="Статус: Загрузите датасет Excel для обучения", font_size='14sp', halign='center')
        self.layout.add_widget(self.status_label)
        
        btn_load = Button(text="Загрузить Excel и обучить модель", size_hint_y=None, height='60dp')
        btn_load.bind(on_press=self.open_file_chooser)
        self.layout.add_widget(btn_load)
        
        btn_calc = Button(text="Оперативная проверка поездки", size_hint_y=None, height='60dp')
        btn_calc.bind(on_press=lambda x: setattr(self.manager, 'current', 'calc_screen'))
        self.layout.add_widget(btn_calc)
        
        btn_logout = Button(text="Выйти из аккаунта", size_hint_y=None, height='50dp', background_color=(0.7, 0.2, 0.2, 1))
        btn_logout.bind(on_press=self.logout)
        self.layout.add_widget(btn_logout)
        
        self.add_widget(self.layout)
        self.update_status()

    def update_status(self):
        m = load_model()
        if m["is_trained"]:
            self.status_label.text = f"Модель обучена!\nR2: {m['r2']:.4f}\nWeights: W={m['coef_weight']:.2f}, S={m['coef_speed']:.2f}"

    def open_file_chooser(self, instance):
        content = BoxLayout(orientation='vertical')
        chooser = FileChooserListView(path='/sdcard' if os.path.exists('/sdcard') else '.')
        content.add_widget(chooser)
        
        btn_layout = BoxLayout(size_hint_y=None, height='50dp', spacing=10)
        btn_select = Button(text="Выбрать файл")
        btn_cancel = Button(text="Отмена")
        
        btn_layout.add_widget(btn_select)
        btn_layout.add_widget(btn_cancel)
        content.add_widget(btn_layout)
        
        popup = Popup(title="Выберите файл Excel (.xlsx)", content=content, size_hint=(0.9, 0.9))
        
        def select_file(inst):
            if chooser.selection:
                res = train_model_from_excel(chooser.selection[0])
                if res["success"]:
                    self.update_status()
                    self.show_popup("Успех", f"Модель переобучена на {res['total_rows']} строках!")
                else:
                    self.show_popup("Ошибка", res["error"])
                popup.dismiss()
                
        btn_select.bind(on_press=select_file)
        btn_cancel.bind(on_press=popup.dismiss)
        popup.open()

    def show_popup(self, title, text):
        p = Popup(title=title, content=Label(text=text), size_hint=(0.8, 0.4))
        p.open()

    def logout(self, instance):
        self.manager.get_screen('login').login_input.text = ""
        self.manager.get_screen('login').pass_input.text = ""
        self.manager.current = 'login'

class DispatcherMainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        layout.add_widget(Label(text="ПАНЕЛЬ ДИСПЕТЧЕРА", font_size='18sp', bold=True))
        
        btn_calc = Button(text="Проверить расход поездки", size_hint_y=None, height='60dp')
        btn_calc.bind(on_press=lambda x: setattr(self.manager, 'current', 'calc_screen'))
        layout.add_widget(btn_calc)
        
        btn_logout = Button(text="Выйти из аккаунта", size_hint_y=None, height='50dp', background_color=(0.7, 0.2, 0.2, 1))
        btn_logout.bind(on_press=self.logout)
        layout.add_widget(btn_logout)
        
        self.add_widget(layout)

    def logout(self, instance):
        self.manager.get_screen('login').login_input.text = ""
        self.manager.get_screen('login').pass_input.text = ""
        self.manager.current = 'login'

class CalcScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        self.input_w = TextInput(hint_text="Вес груза (тонн)", multiline=False, input_filter='float')
        self.input_s = TextInput(hint_text="Средняя скорость (км/ч)", multiline=False, input_filter='float')
        self.input_f = TextInput(hint_text="Фактический расход (литров)", multiline=False, input_filter='float')
        
        layout.add_widget(self.input_w)
        layout.add_widget(self.input_s)
        layout.add_widget(self.input_f)
        
        btn_run = Button(text="Выполнить расчет", size_hint_y=None, height='50dp', background_color=(0.2, 0.5, 0.8, 1))
        btn_run.bind(on_press=self.run_calc)
        layout.add_widget(btn_run)
        
        self.result_label = Label(text="Введите параметры поездки", font_size='14sp', halign='center')
        layout.add_widget(self.result_label)
        
        # Исправленный блок кнопок экспорта
        btn_layout = BoxLayout(size_hint_y=None, height='50dp', spacing=10)
        self.btn_export = Button(text="Экспорт в PDF", on_press=self.save_report_pdf)
        btn_back = Button(text="Назад", on_press=self.go_back)
        
        btn_layout.add_widget(self.btn_export)
        btn_layout.add_widget(btn_back)
        layout.add_widget(btn_layout)
        
        self.add_widget(layout)
        self.last_report = ""

    def run_calc(self, instance):
        try:
            w = float(self.input_w.text)
            s = float(self.input_s.text)
            f = float(self.input_f.text)
            
            res = calculate_single_trip(w, s, f)
            
            self.last_report = (f"РЕЗУЛЬТАТ АНАЛИЗА ПОЕЗДКИ:\n"
                                f"----------------------------------------\n"
                                f"Прогноз нормы: {res['predicted']:.2f} л.\n"
                                f"Критический порог: {res['upper_bound']:.2f} л.\n"
                                f"Фактический расход: {f:.2f} л.\n"
                                f"Перерасход: {res['extra_fuel']:.2f} л.\n"
                                f"Экологический ущерб: {res['damage']:.2f} руб.")
            self.result_label.text = self.last_report
        except ValueError:
            self.result_label.text = "Ошибка: Заполните все поля числами!"

    def save_report_pdf(self, instance):
        if not self.last_report:
            return
        
        # Сохранение в стандартную публичную папку Downloads телефона
        download_path = "/sdcard/Download"
        if not os.path.exists(download_path):
            download_path = App.get_running_app().user_data_dir
            
        file_path = os.path.join(download_path, "fuel_trip_report.pdf")
        success = export_to_pdf_android(file_path, self.last_report)
        
        p = Popup(title="Экспорт", content=Label(text=f"Сохранено в:\n{file_path}" if success else "Ошибка записи PDF"), size_hint=(0.8, 0.4))
        p.open()

    def go_back(self, instance):
        self.input_w.text = ""
        self.input_s.text = ""
        self.input_f.text = ""
        self.result_label.text = "Введите параметры поездки"
        self.last_report = ""
        
        # Возврат на экран в зависимости от того, кто авторизован
        if self.manager.previous_twi == 'admin':
            self.manager.current = 'admin_main'
        else:
            # Динамическое определение роли
            self.manager.current = 'login' 

class FuelApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(AdminMainScreen(name='admin_main'))
        sm.add_widget(DispatcherMainScreen(name='dispatcher_main'))
        sm.add_widget(CalcScreen(name='calc_screen'))
        return sm

if __name__ == '__main__':
    FuelApp().run()