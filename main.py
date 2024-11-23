import json
import re
import requests
import os
import subprocess
import sys

from bs4 import BeautifulSoup
from pathlib import Path


class Visualizator:
    # ssl._create_default_https_context = ssl._create_unverified_context
    # package = "https://pkgs.alpinelinux.org/package/edge/community/x86_64/buildah"

    visualizer = ''
    package = ''
    result = ''
    debug_mode = True

    def log(self, message: object):
        if self.debug_mode:
            print(message)

    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            params = json.load(f)
            if not params:
                print('Error when attempting to load the settings file.')
            else:
                # Подключение программы-визуализатора
                temp = Path(params['visualizer']).resolve()
                if not Path.is_file(temp):
                    print('Cannot reach virtualizer')
                else:
                    self.visualizer = temp
                # Задание директории для вывода файла-результата
                temp = Path(params['result']).resolve()
                if not temp.parent.exists():
                    print(f'No such directory: "{self.result}". The file will be exported to the current directory.')
                    self.result = Path.cwd() / 'result.dot'
                else:
                    self.result = temp
                # Задание анализируемого пакета
                self.package = params['package']

    def parse(self):
        # Функция разбора страницы
        def load_page(url):
            for counter in range(3):
                try:
                    page = requests.get(url).text
                    doc = BeautifulSoup(page, 'html.parser')
                    return doc
                except requests.exceptions as e:
                    pass
            print('Ошибка чтения страницы. Проверьте подключение к интернету и повторите попытку запуска программы.')
            exit()

        links = [self.package]  # Страницы, которые нужно обойти, начиная с корня
        deps = {}

        while len(links) != 0:
            current_page = load_page(links[0])  # Загружаем следующую страницу
            current_pack = current_page.find(id='package').find_next('td').text  # Рассматриваемый пакет

            if deps.get(current_pack) is None:  # Если пакета ещё нет в списке зависимостей
                deps[current_pack] = []  # Инициализация массива зависимостей
                self.log(f'{current_pack} — {links[0]}')

                package_list = current_page.find_all('details')[0].find_all('li')  # Зависимости данного пакета
                for i in package_list:
                    package_name = re.sub('[\n\s]+', '', i.text)  # Имя проверяемой графы "Depends"

                    if package_name != 'None':  # Проверяем, если есть зависимости
                        href = 'https://pkgs.alpinelinux.org' + i.a.attrs['href']
                        links.append(href)  # Добавляем ссылку на страницу зависимости в очередь
                        deps[current_pack].append(package_name)

                    self.log(f'\t{package_name}')

            links.pop(0)

        links.clear()
        self.log(deps)
        return deps

    def set_dependencies(self):
        # Больше не используется. Ранее применялась вместе с graphviz для создания зависимостей
        # def escape(item):
        #     return re.sub('\W+', '', item)

        deps = self.parse()
        graph = ['digraph {', '}']

        for i in deps:
            if len(deps[i]) != 0:
                for j in deps.get(i):
                    graph.insert(len(graph) - 1, f'\t"{i}" -> "{j}"')

        try:
            result_file = open(self.result, 'w')
            result_file.write('\n'.join(graph))
            result_file.close()
            return True
        # По-хорошему, данная проверка здесь излишняя
        except FileNotFoundError:
            print(f'Файл {self.result} не найден.')
        except IOError:
            print(f'Ошибка при открытии файла "{self.result}".')
        return False

        # graph = graphviz.Digraph()
        # graph.node(escape(j), j)
        # graph.edge(escape(i), escape(j))
        # graph.render('dependencies', format='png', cleanup=True)

    def graph_render(self):
        render_path = Path('C:/Users/Inter/Desktop/result.png')
        try:
            subprocess.run([self.visualizer, self.result, '-T', 'png', '-o', render_path], check=True)
            if self.debug_mode:
                os.startfile(render_path)
            return True
        except subprocess.CalledProcessError as err:
            print("Exception when starting visualizer process:", err)
        return False


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: program <config_file>")
        sys.exit(1)

    config = sys.argv[1]

    instance = Visualizator(config)
    instance.set_dependencies()
    instance.graph_render()
