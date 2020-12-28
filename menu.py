from main import MangaScraper


class Menu:
    def __init__(self, scraper=None):
        self.scraper = MangaScraper().init(False, 1) if scraper is None else scraper

    def search(self, name):
        def already_in(dict_, index):
            for obj in dict_:
                if obj.get('index') == index:
                    return True

        list_of_names = name.split(' ')
        list_searched = []

        for item in self.scraper.all_mangas:
            """
            for name in list_of_names:
                if name.upper() in item.get('name').upper():
                    if not already_in(list_searched, item.get('index')):
                        list_searched.append(item)
        
            """
            if name.upper() in item.get('name').upper():
                list_searched.append(item)

        return list_searched

    def download(self, option):
        chapter = [self.scraper.get_by_index(option.get('index'), 'chapter')]

        MangaScraper([option], chapter).download_all_mangas()

    def run(self):
        while 1:
            print('BEM VINDO, DIGITE O NOME DE ALGUM MANGÁ OU DIGITE 0 PARA SAIR')
            option = input('>> ')

            if option == '0':
                break

            list_manga = self.search(option)

            print('ESCOLHA UMA OPÇÃO')
            print('0 - Cancelar')

            for i in range(len(list_manga)):
                print('%d - %s' % (i + 1, list_manga[i].get('name')))
            try:
                option = int(input('>> '))
                if option != 0:
                    self.download(list_manga[option - 1])

            except ValueError:
                print('VALOR INCORRETO, REINICIANDO PROGRAMA')


if __name__ == '__main__':
    Menu(MangaScraper().init(True)).run()
