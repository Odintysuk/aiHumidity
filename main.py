"""


#013e6d - blue from logo
#5b6c73 - grey from logo
#3d3d3d - grey background logo


"""
# Screen size configs --temporary--
from kivy.config import Config
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')

# imports
import pandas as pd
import math
import os
import numpy as np
from random import uniform
from kivy.lang import Builder
from kivymd.uix.button import MDButton
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogSupportingText, MDDialogButtonContainer
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.core.text import LabelBase

os.environ['KIVY_IMAGE'] = 'pil'

KV = (""" 
<MainScreen>:
    id: main
    md_bg_color: self.theme_cls.backgroundColor
    FitImage:
        source: 'bkg.jpg'
    
    MDBoxLayout:
        id: boxlabel
        adaptive_size: False
        size_hint: 1, .5
        orientation: 'horizontal'
        padding: 20
        pos: 0, root.height - root.height/2
        
        MDBoxLayout:
            id:box_report
            radius: 40
            md_bg_color: self.theme_cls.primaryColor
            adaptive_size: True
            size_hint: 1, 1
            
            MDLabel:
                id: report
                width: self.width
                pos_hint: {'center_x': .5, 'center_y': .45}
                halign: 'center'
                theme_font_name: 'Custom'
                font_name: 'MOSCOW2024'
                font_style: 'Display'
                role: 'large'
                text: ''
        
    MDBoxLayout:
        id: box
        adaptive_size: True
        size_hint: 1, .5
        orientation: 'vertical'
        
        MDBoxLayout:
            id: box_fields
            adaptive_size: True
            size_hint: 1, None
            padding: 25
            spacing: 5
            orientation: 'horizontal'
                    
            canvas.before:
                Color:
                    rgb: .36, .42, .45
                RoundedRectangle:
                    size: self.width-40, self.height-40
                    pos: self.x+20, self.y+20
                    radius: [20, 20, 0, 0]
                    
            MDTextField:
                id: dry
                radius: 15
                mode: 'filled'
                font_style: 'Title'
                role: 'large'
                input_filter: 'float'
                set_text: root.set_text
                
                MDTextFieldHintText:
                    text: 'Dry' 
                        
            MDTextField:
                id: wet
                radius: 15
                mode: 'filled'
                font_style: 'Title'
                role: 'large'
                input_filter: 'float'
                set_text: root.set_text
                MDTextFieldHintText:
                    text: 'Wet'
        
        MDFloatLayout:
            id: float_calc
            size_hint: 1, None
            padding: [25, 0, 0, 25]
            height: root.ids.box_fields.height-25
            
            canvas.before:
                Color:
                    rgb: .36, .42, .45
                RoundedRectangle:
                    size: self.width-40, self.height-15
                    pos: self.x+20, self.y+20
                    radius: [0, 0, 20, 20]
                    
            MDButton:
                id: calc
                # adaptive_size: True
                size_hint_x: None
                on_release: root.getdata(root.ids.dry.text, root.ids.wet.text)
                radius: [15, 15, 15, 15]
                height: root.ids.dry.height
                width: root.ids.float_calc.width-150
                pos_hint: {'top': 1, 'center_x': .5}
                min_size_x: 150
            
                MDButtonText:
                    text: 'Расчитать влажность'
                    adaptive_size: True
                    pos_hint: {'top': 1, 'center_x': .5}
                    color: '3d3d3d'
                
        MDBoxLayout:
            id: bottombox
            size_hint_x: 1
            pos_hint: {'center_x': .5}
            spacing: 15
            orientation: 'horizontal'
        
            MDButton:
                id: randomtest
                radius: 10
                on_release: root.randomtest()
                MDButtonText:
                    text: 'тест. случайное'
                    color: '3d3d3d'

                    
<SecondScreen>:
    id: second
    md_bg_color: self.theme_cls.backgroundColor
    
    MDGridLayout:
        id: grid
        cols: 13
        set: root.build()

MDBoxLayout:
    orientation: "vertical"
    md_bg_color: self.theme_cls.backgroundColor

    MDScreenManager:
        id: screen_manager

        MainScreen:
            name: 'main'
        SecondScreen:
            name: 'second'


    MDNavigationBar:
        on_switch_tabs: app.on_switch_tabs(*args)
        size_hint_y: .1

        MDNavigationItem:
            on_press: root.ids.screen_manager.transition.direction = 'right'
            text: 'main'
            active: True
            MDNavigationItemIcon:
                icon: 'calculator'

        MDNavigationItem:
            on_press: root.ids.screen_manager.transition.direction = 'left'
            text: 'second'
            MDNavigationItemIcon:
                icon: 'table-large'
            
"""
)


def error():
    """Открытие окна ошибки
    Вызывается при введении некорректных данных в поле ввода тарифов
    MDTextField расположенных в MDNavigationDrawer

    """

    def errorclose(self):
        """Закрывает окно ошибки"""
        dialogerror.dismiss()
        return

    from kivymd.uix.button import MDButtonText
    dialogerror = MDDialog(
        # ---- Headline text -----
        MDDialogHeadlineText(
            text='Ошибка',
            halign='center',
        ),
        # ---- Support text ----
        MDDialogSupportingText(
            text='Проверьте введенные данные',
        ),
        #  ---- Button container ----
        MDDialogButtonContainer(
            MDButton(
                MDButtonText(
                    text='Ok',
                ),
                on_release=errorclose
            )
        )
    )
    dialogerror.open()
    return


class MainScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__( **kwargs)
        # чтение таблицы csv
        self.table = pd.read_csv('psytable.csv',
                                 index_col=0,
                                 header=0).fillna(0)


    def set_text(self, instance, text):

        try:
            if text == '':
                return
            if instance == self.ids.dry:
                if 0 <= float(text) <= 30:
                    instance.error = False
                    self.set_text(self.ids.wet, self.ids.wet.text)
                else:
                    instance.error = True

            if instance == self.ids.wet:
                if ((0 <= (float(self.ids.dry.text) - float(text)) <= 11)
                        and (float(text) <= float(self.ids.dry.text))):
                    instance.error = False
                else:
                    instance.error = True
        except Exception as e:
            print(e)

    def on_error(self):
        pass

    def getdata(self, dry, wet):
        """
        Определяет переменные dry_t и wet_t из textfields
        Считывает таблицу данных csv
        Выделяет фрагмент таблицы с ближайшими значениями столбцов и строк к аргументам
        Преобразует данные фрагмента во фрейм со значениями столбцов: строка, столбец, значение ячейки
        Создает модель линейной регрессии на основе датафрейма
        Прогнозирует значение влажности (h) исходя из аргументов (dry_t, wet_t)

            Args:
                dry: float() - значение показаний сухого термометра
                wet: float() - значение показаний влажного термометра
            Returns:
                h: float() - значение влажности
        """
        try:
            dry_t = float(dry)
            wet_t = float(wet)
            delta_t = dry_t - wet_t

            # создание фрагмента таблицы с ближайшими столбцами и строками к dry_t и delta_t
            table_cut = self.table[self.table.columns[math.floor(delta_t):math.ceil(delta_t) + 1]]
            table_cut = table_cut.loc[list({math.floor(dry_t), math.ceil(dry_t)})]
            # интерполяция табличных значений по delta_t для ближайших  табличных значений к dry_t
            interp_1 = np.interp([delta_t], table_cut.columns, table_cut.loc[min(table_cut.index)])[0]
            interp_2 = np.interp([delta_t], table_cut.columns, table_cut.loc[max(table_cut.index)])[0]
            # Выравнивание длин списков для интерполяции
            fp = table_cut.index.to_list()
            xp = list([interp_1, interp_2])[:len(fp)]
            # интерполяция значений по interp_1 и interp_2 для dry_t
            interp = np.interp(dry_t, fp, xp)
            h = interp.round(1)
            # вывод значения h в качестве текста MDLabel
            self.ids.report.text = str(h)
            return h

        except Exception as e:
            error()
            print(e.__class__.__name__, e)
        return

    def randomtest(self):
        '''
        подбирает случайные значения dry_t, wet_t в диапазоне
        рассчитывает значение h, которое должно находиться в заданном диапазоне
        заполняет полученные значения в полях textfields и выводит результат влажности

            Args:
                None
            Returns:
                None
        '''
        dry_t = float()
        wet_t = float()
        h = float()
        while not (70 < h < 80):
            dry_t = round(uniform(17, 21), 1)
            wet_t = round(uniform(15, dry_t), 1)
            h = self.getdata(dry_t, wet_t)

        self.ids.dry.text = str(dry_t)
        self.ids.wet.text = str(wet_t)
        self.ids.report.text = str(h)
        return


class SecondScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__( **kwargs)
        self.table = MainScreen().table

    def build(self):
        # добавляем первым столбцом значение термометра
        self.table.insert(0, ' ', self.table.index)
        # удаляем столбцы со значениями только 100 и 0
        self.table = self.table.drop([self.table.columns[1], self.table.columns[12]], axis=1)
        # убираем лишние нули после запятой (переводим в int)
        self.table = self.table.astype(int)
        for i in self.table.columns:
            xs = '\n'.join([i] + list(self.table[i].astype(str)))
            self.ids.grid.add_widget(MDLabel(text=xs,
                                             padding=30,
                                             font_style='Label',
                                             role='small'))


class aiHumidity(MDApp):

    def build(self):
        LabelBase.register(
            name="MOSCOW2024",
            fn_regular="MOSCOW2024.otf",
        )
        return Builder.load_string(KV)

    def on_switch_tabs(self, *args):
        self.root.ids.screen_manager.current = args[1].text


if __name__ == "__main__":
    aiHumidity().run()