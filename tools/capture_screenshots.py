#!/usr/bin/env python3

# Copyright 2026 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""
Generate store screenshots for all devices and interface languages.

  python tools/capture_screenshots.py
  SCREENSHOT_DEVICES="iPhone 15 Pro,Pixel 7a" SCREENSHOT_LOCALES=EN,DE python tools/capture_screenshots.py
  SCREENSHOT_STEPS=3_category SKIP_EXISTANT=true SCREENSHOT_WORKERS=4 python tools/capture_screenshots.py

Every screenshot starts the app (in light mode) with an empty profile, so personal data never leaks
into the images. The demo content is entered through the app's own forms before each screenshot:
language pairs (*-PL), categories in the interface language and 10 words of the selected pair.
"""

import atexit
import os
import shutil
import sys
import tempfile
from pathlib import Path

from kivy_screenshot_generator import ScreenshotConfig, ScreenshotGenerator

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / 'src'

sys.path.insert(0, str(SRC_DIR))
from kivy.uix.screenmanager import NoTransition  # noqa: E402
from l18n.labels import labels  # noqa: E402

TARGET_LOCALE = 'PL'
SOURCE_LOCALES = [
    'AR', 'AZ', 'BE', 'CS', 'DE', 'EN', 'ES', 'FA', 'FR', 'HI', 'ID', 'IT', 'JA',
    'KA', 'KO', 'NL', 'PT-BR', 'PT-PT', 'RO', 'RU', 'TR', 'UK', 'UZ', 'ZH-CN', 'ZH-TW',
]
# Interface languages without their own pair (Polish) study from English
FALLBACK_SOURCE_LOCALE = 'EN'

# General, Literature, Common
CATEGORIES = {
    'AR': ['عام', 'أدب', 'يومي'],
    'AZ': ['Ümumi', 'Ədəbiyyat', 'Gündəlik'],
    'BE': ['Агульнае', 'Літаратура', 'Паўсядзённае'],
    'CS': ['Obecné', 'Literatura', 'Každodenní'],
    'DE': ['Allgemein', 'Literatur', 'Alltägliches'],
    'EN': ['General', 'Literature', 'Common'],
    'ES': ['General', 'Literatura', 'Cotidiano'],
    'FA': ['عمومی', 'ادبیات', 'روزمره'],
    'FR': ['Général', 'Littérature', 'Courant'],
    'HI': ['सामान्य', 'साहित्य', 'दैनिक'],
    'ID': ['Umum', 'Sastra', 'Sehari-hari'],
    'IT': ['Generale', 'Letteratura', 'Quotidiano'],
    'JA': ['一般', '文学', '日常'],
    'KA': ['ზოგადი', 'ლიტერატურა', 'ყოველდღიური'],
    'KO': ['일반', '문학', '일상'],
    'NL': ['Algemeen', 'Literatuur', 'Dagelijks'],
    'PL': ['Ogólne', 'Literatura', 'Codzienne'],
    'PT-BR': ['Geral', 'Literatura', 'Cotidiano'],
    'PT-PT': ['Geral', 'Literatura', 'Quotidiano'],
    'RO': ['General', 'Literatură', 'Cotidian'],
    'RU': ['Общее', 'Литература', 'Повседневное'],
    'TR': ['Genel', 'Edebiyat', 'Günlük'],
    'UK': ['Загальне', 'Література', 'Повсякденне'],
    'UZ': ['Umumiy', 'Adabiyot', 'Kundalik'],
    'ZH-CN': ['通用', '文学', '日常'],
    'ZH-TW': ['通用', '文學', '日常'],
}

WORDS = {
    'PL': ['woda', 'chleb', 'dom', 'słońce', 'książka', 'przyjaciel', 'jabłko', 'kot', 'pies', 'miasto'],
    'AR': ['ماء', 'خبز', 'بيت', 'شمس', 'كتاب', 'صديق', 'تفاحة', 'قطة', 'كلب', 'مدينة'],
    'AZ': ['su', 'çörək', 'ev', 'günəş', 'kitab', 'dost', 'alma', 'pişik', 'it', 'şəhər'],
    'BE': ['вада', 'хлеб', 'дом', 'сонца', 'кніга', 'сябар', 'яблык', 'кот', 'сабака', 'горад'],
    'CS': ['voda', 'chléb', 'dům', 'slunce', 'kniha', 'přítel', 'jablko', 'kočka', 'pes', 'město'],
    'DE': ['Wasser', 'Brot', 'Haus', 'Sonne', 'Buch', 'Freund', 'Apfel', 'Katze', 'Hund', 'Stadt'],
    'EN': ['water', 'bread', 'house', 'sun', 'book', 'friend', 'apple', 'cat', 'dog', 'city'],
    'ES': ['agua', 'pan', 'casa', 'sol', 'libro', 'amigo', 'manzana', 'gato', 'perro', 'ciudad'],
    'FA': ['آب', 'نان', 'خانه', 'خورشید', 'کتاب', 'دوست', 'سیب', 'گربه', 'سگ', 'شهر'],
    'FR': ['eau', 'pain', 'maison', 'soleil', 'livre', 'ami', 'pomme', 'chat', 'chien', 'ville'],
    'HI': ['पानी', 'रोटी', 'घर', 'सूरज', 'किताब', 'दोस्त', 'सेब', 'बिल्ली', 'कुत्ता', 'शहर'],
    'ID': ['air', 'roti', 'rumah', 'matahari', 'buku', 'teman', 'apel', 'kucing', 'anjing', 'kota'],
    'IT': ['acqua', 'pane', 'casa', 'sole', 'libro', 'amico', 'mela', 'gatto', 'cane', 'città'],
    'JA': ['水', 'パン', '家', '太陽', '本', '友達', 'りんご', '猫', '犬', '都市'],
    'KA': ['წყალი', 'პური', 'სახლი', 'მზე', 'წიგნი', 'მეგობარი', 'ვაშლი', 'კატა', 'ძაღლი', 'ქალაქი'],
    'KO': ['물', '빵', '집', '태양', '책', '친구', '사과', '고양이', '개', '도시'],
    'NL': ['water', 'brood', 'huis', 'zon', 'boek', 'vriend', 'appel', 'kat', 'hond', 'stad'],
    'PT-BR': ['água', 'pão', 'casa', 'sol', 'livro', 'amigo', 'maçã', 'gato', 'cachorro', 'cidade'],
    'PT-PT': ['água', 'pão', 'casa', 'sol', 'livro', 'amigo', 'maçã', 'gato', 'cão', 'cidade'],
    'RO': ['apă', 'pâine', 'casă', 'soare', 'carte', 'prieten', 'măr', 'pisică', 'câine', 'oraș'],
    'RU': ['вода', 'хлеб', 'дом', 'солнце', 'книга', 'друг', 'яблоко', 'кот', 'собака', 'город'],
    'TR': ['su', 'ekmek', 'ev', 'güneş', 'kitap', 'arkadaş', 'elma', 'kedi', 'köpek', 'şehir'],
    'UK': ['вода', 'хліб', 'дім', 'сонце', 'книга', 'друг', 'яблуко', 'кіт', 'собака', 'місто'],
    'UZ': ['suv', 'non', 'uy', 'quyosh', 'kitob', 'doʻst', 'olma', 'mushuk', 'it', 'shahar'],
    'ZH-CN': ['水', '面包', '房子', '太阳', '书', '朋友', '苹果', '猫', '狗', '城市'],
    'ZH-TW': ['水', '麵包', '房子', '太陽', '書', '朋友', '蘋果', '貓', '狗', '城市'],
}

SELECT_ICON = chr(0xF012C)

_profile_dir = None


def init(device, config, locale):
    global _profile_dir
    _profile_dir = tempfile.mkdtemp(prefix='tlum_screenshot_')
    atexit.register(shutil.rmtree, _profile_dir, ignore_errors=True)


def get_app():
    # The app resolves templates and assets relative to `src`
    os.chdir(SRC_DIR)
    from main import MainApp

    class ScreenshotApp(MainApp):
        @property
        def user_data_dir(self):
            return _profile_dir

    app = ScreenshotApp()
    app.update_locale(gen.job.locale)
    app.toggle_theme_mode(False)
    return app


def source_locale(app):
    return app.locale if app.locale in SOURCE_LOCALES else FALLBACK_SOURCE_LOCALE


# Demo content, entered through the same screens a user fills in

async def add_language_pairs(tester):
    screen = tester.app.root.get_screen('language_pair_add_screen')
    for locale in SOURCE_LOCALES:
        await tester.show_screen('language_pair_add_screen')
        screen.select_from_language(locale)
        screen.select_to_language(TARGET_LOCALE)
        screen.save_language_pair()
        assert not screen.status_text, screen.status_text
    await tester.pump_and_settle()


async def add_categories(tester):
    app = tester.app
    app.locale_from, app.locale_to = source_locale(app), TARGET_LOCALE
    screen = app.root.get_screen('category_add_screen')
    for name in CATEGORIES[app.locale]:
        await tester.show_screen('category_add_screen')
        screen.category_name_text = name
        screen.save_category()
        assert not screen.status_text, screen.status_text
    await tester.pump_and_settle()


async def add_words(tester):
    app = tester.app
    screen = app.root.get_screen('vocabulary_add_screen')
    category = CATEGORIES[app.locale][0]
    for origin, translation in zip(WORDS[app.locale_from], WORDS[app.locale_to]):
        await tester.show_screen('vocabulary_add_screen')
        screen.category_text = category
        screen.origin_text = origin
        screen.translation_text = translation
        screen.save_vocabulary_item()
        assert not screen.status_text, screen.status_text
    await tester.pump_and_settle()


# Navigation through the main screen, by tapping its rows

def main_row(tester, text):
    return tester.find(lambda w: type(w).__name__ == 'RootItemWidget' and w.text == text)


def row_button(tester, row, text):
    return tester.find(lambda w: w.parent is row and text in getattr(w, 'text', ''))


async def select(tester, text):
    row = main_row(tester, text)
    # Portrait rows show the icon only
    await tester.tap(row_button(tester, row, SELECT_ICON))
    await tester.pump_and_settle()


async def open_categories(tester):
    app = tester.app
    pair = app._container.config_repository().get_language_pair(source_locale(app), TARGET_LOCALE)
    await select(tester, pair['text'])


async def open_games(tester):
    await open_categories(tester)
    await select(tester, CATEGORIES[tester.app.locale][0])


def play(game_key):
    async def step(tester):
        await prepare(tester)
        await open_games(tester)
        row = main_row(tester, game_key)
        await tester.tap(row_button(tester, row, tester.app._('button_play', tester.app.locale)))
        # The game opens after a loading screen
        await tester.pump_and_settle(2)
    return step


async def prepare(tester):
    # Data entry is not part of the screenshots: skip the screen animations
    manager = tester.app.root
    transition, manager.transition = manager.transition, NoTransition()
    try:
        await add_language_pairs(tester)
        await add_categories(tester)
        await add_words(tester)
        await tester.show_screen('main_screen')
    finally:
        manager.transition = transition


# Steps

async def show_main(tester):
    await prepare(tester)


async def open_language_pair(tester):
    await prepare(tester)
    await tester.show_screen('language_pair_add_screen')
    await tester.tap(tester.find_by_id('from_language'))
    await tester.pump_and_settle()
    # The search field of the opened dropdown is focused automatically
    await tester.enter_text(tester.find(lambda w: getattr(w, 'focus', False)), 'en')


async def show_categories(tester):
    await prepare(tester)
    await open_categories(tester)


gen = ScreenshotGenerator(
    locales=list(labels),
    fn_init=init,
    fn_get_app=get_app,
    config=ScreenshotConfig(output_directory=str(PROJECT_ROOT / 'screenshots')),
)
gen.inject('1_main', before=show_main)
gen.inject('2_language_pair', before=open_language_pair)
gen.inject('3_category', before=show_categories)
gen.inject('4_cards', before=play('game_cards'))
gen.inject('5_harmonica', before=play('game_harmonica'))
gen.inject('6_harmonica_acoustic', before=play('game_harmonica_acoustic'))
gen.inject('7_articulation', before=play('game_articulation'))

if __name__ == '__main__':
    gen.run()
