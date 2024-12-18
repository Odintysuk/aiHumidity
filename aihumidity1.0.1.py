"""
Программа приложения под android для расчета влажности
по экспериментальным значениям сухого и влажного термометров.
Присутствует возможность случайного подбора значений и расчет влажности в необходимом диапазоне

v.1.0.1

"""

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
    
    MDBoxLayout:
        id: boxlabel
        md_bg_color: '5b6c73'
        adaptive_size: False
        size_hint: 1, .2
        id: box_label
        orientation: 'horizontal'
        pos: 0, root.height - root.height/5
        
        MDLabel:
            md_bg_color: '3d3d3d'
            theme_font_name: 'Custom'
            font_name: 'Beladonna_Modern'
            text: 'ПСИХРОМЕТР'
            halign: 'center'
            valign: 'center'
            theme_text_color: 'Custom'
            text_color: 'black'
            font_style: 'Display'
            role: 'small'
        
    MDBoxLayout:
        id: box
        # md_bg_color: self.theme_cls.backgroundColor
        adaptive_size: True
        size_hint: 1, .8
        # pos: 0, self.height - self.height/1.5
        orientation: 'vertical'
        padding: 30
        spacing: 20
        
        MDBoxLayout:
            size_hint: 1, .2 
            pos_hint: {'center_x': 1}
            
            MDLabel:
                id: report
                theme_font_name: 'Custom'
                font_name: 'Beladonna_Modern'
                text: ''
            
        MDTextField:
            id: dry
            mode: 'outlined'
            input_filter: 'float'
            set_text: root.set_text
            MDTextFieldHintText:
                text: 'Показания сухого'    
                    
        MDTextField:
            id: wet
            mode: 'outlined'
            input_filter: 'float'
            set_text: root.set_text
            MDTextFieldHintText:
                text: 'Показания влажного'
            
        MDButton:
            id: calc
            on_release: root.getdata(root.ids.dry.text, root.ids.wet.text)
            radius: 10
            pos_hint: {'center_x': .5}
            MDButtonText:
                text: 'Расчитать влажность'
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
        # Headline text
        MDDialogHeadlineText(
            text='Ошибка',
            halign='center',
        ),
        # Support text
        MDDialogSupportingText(
            text='Проверьте введенные данные',
        ),
        # Button container
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
        """Проверка введенных данных в полях MDTextField на соответствие некоторым условиям
        Активирует или деактивирует статус ошибки в поле ввода MDTextField

        """
        try:
            if text == '':
                return
            if instance == self.ids.dry:
                # значения сухого от 0 до 30
                if 0 <= float(text) <= 30:
                    instance.error = False
                    self.set_text(self.ids.wet, self.ids.wet.text)
                else:
                    instance.error = True

            if instance == self.ids.wet:
                # значения разницы сухого и влажного должны быть от 0 до 11
                # при этом показания влажного не больше сухого
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
        """
        Подбирает случайные значения dry_t, wet_t в "допустимом" диапазоне
        рассчитывает значение h, которое должно находиться в заданном диапазоне
        заполняет полученные значения в полях textfields и выводит результат влажности

            Args:
                None
            Returns:
                None
        """

        dry_t = float()
        wet_t = float()
        h = float()

        # цикл подбора случайных значений в ограниченных диапазонах
        # при которых рассчитанная влажность находится в указанном диапазоне
        while not (70 < h < 80):
            dry_t = round(uniform(17, 21), 1)   # допустимый диапазон сухого термометра
            wet_t = round(uniform(15, dry_t), 1)    # диапазон влажного термометра. зависит от зн. сухого
            # расчет влажности по случайным значениям
            h = self.getdata(dry_t, wet_t)
        # заполнение подобранных значений в поля ввода данных для наглядности примера расчета
        self.ids.dry.text = str(dry_t)
        self.ids.wet.text = str(wet_t)
        self.ids.report.text = str(h)
        return


class SecondScreen(MDScreen):
    """Второй экран для отображения общей психрометрической таблицы

    """
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
            name="Beladonna_Modern",
            fn_regular="Beladonna_Modern.ttf",
        )
        return Builder.load_string(KV)

    def on_switch_tabs(self, *args):
        self.root.ids.screen_manager.current = args[1].text


if __name__ == "__main__":
    aiHumidity().run()