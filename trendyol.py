import requests
import tkinter as tk

from bs4 import BeautifulSoup


class Window:
    def __init__(self):
        self.root = tk.Tk()
        self.links = []

        self.reqs = [requests.get(i) for i in self.links]
        self.sources = [BeautifulSoup(req.content, 'html.parser') for req in self.reqs]

        self.prices = [Window.find_lowest_price(source, 'span', attrs={'class': 'prc-dsc'}) for source in self.sources]
        self.prices_og = [Window.find_lowest_price(source, 'span', attrs={'class': 'prc-org'}) for source in self.sources]
        self.h1 = [source.find('h1', attrs={'class': 'pr-new-br'}) for source in self.sources]

        self.labels: list[tk.Label] = []

        self.link_to_add = tk.StringVar()
        self.link_entry = tk.Entry(self.root, textvariable=self.link_to_add, width=100)

        self.add_btn = tk.Button(self.root, text='Add link', command=self.add_link)
        for label in self.labels:
            label.pack()

        self.link_entry.pack()
        self.add_btn.pack()

    def add_link(self):
        self.links.append(self.link_to_add.get())
        self.link_to_add.set('')

        self.reqs = [requests.get(i) for i in self.links]
        self.sources = [BeautifulSoup(req.content, 'html.parser') for req in self.reqs]

        self.prices = [self.find_lowest_price(source, 'span', attrs={'class': 'prc-dsc'}) for source in self.sources]
        self.prices_og = [source.find('span', attrs={'class': 'prc-org'}) for source in self.sources]
        self.h1 = [source.find('h1', attrs={'class': 'pr-new-br'}) for source in self.sources]
        self.labels.append(tk.Label(self.root, text=('' if self.h1[-1].find('a') is None else self.h1[-1].find('a').text + ' - ') + Window.removesurrounding(self.h1[-1].find('span').text, ' ') + ' - ' + str(self.prices[-1]) + ' TL' + ('' if self.prices_og[-1] is None else ' - Original price: ' + self.prices_og[-1].text.replace('.', '') + f' ({round(100 * ((float(self.prices_og[-1].text.removesuffix(" TL").replace(".", "").replace(",", ".")) / self.prices[-1]) - 1), 2)}% discount)')))

    @staticmethod
    def removesurrounding(string: str, char: str):
        return string.removeprefix(char).removesuffix(char)

    @staticmethod
    def find_lowest_price(soup: BeautifulSoup, tag: str, attrs: dict, price_symbol='TL', with_space: bool = True):
        all_items = soup.find_all(tag, attrs=attrs)
        all_prices = []
        for i, v in enumerate(all_items):
            all_prices.append(float(v.text.removesuffix((' ' if with_space else '') + price_symbol).replace('.', '').replace(',', '.')))

        return Window.list_min(all_prices)

    @staticmethod
    def list_min(lst):

        if len(lst) == 0:
            return 0

        record = lst[0]
        for i in lst:
            if i < record:
                record = i

        return record

    def launch(self):
        def pack_labels():
            for label in self.labels:
                label.pack_forget()
                label.pack()

            self.link_entry.pack_forget()
            self.link_entry.pack()

            self.add_btn.pack_forget()
            self.add_btn.pack()

            self.root.after(1000, pack_labels)

        self.root.after(1000, pack_labels)

        self.root.mainloop()


tp = Window()
tp.launch()
