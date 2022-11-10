import json
import requests
import tkinter as tk
from tkinter import ttk

from bs4 import BeautifulSoup


class Popup:
    def __init__(self, bound, title, message):
        self.root = tk.Toplevel(bound.root)
        self.root.grab_set()
        self.root.title(title)
        self.root.geometry(f'{self.root.winfo_reqwidth() + 48}x{int(self.root.winfo_reqwidth() / (3 / 2))}')
        self.msg = ttk.Label(self.root, text=message)

        self.msg.pack()

    def show(self):
        self.root.mainloop()

    def close(self):
        self.root.destroy()


class PopupOK(Popup):
    def __init__(self, bound, title, message):
        super().__init__(bound, title, message)

        self.ok = ttk.Button(self.root, text='OK', command=self.close)
        self.ok.pack()


class PopupOKCancel(Popup):
    def __init__(self, bound, title, message, ok_func=None):
        super().__init__(bound, title, message)

        self.ok = ttk.Button(self.root, text='OK', command=self.close_ok)
        self.ok_bound = ok_func
        self.ok.pack()

        self.cancel = ttk.Button(self.root, text='Cancel', command=self.close_cancel)
        self.cancel.pack()

    def close(self):
        pass

    def close_ok(self):
        if self.ok_bound is not None:
            self.ok_bound()
        self.root.destroy()

    def close_cancel(self):
        self.root.destroy()


class Window:
    def __init__(self):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.fot = False  # force-overwrite the target

        self.links = []
        with open('targets.json', 'r') as f:
            self.targets = json.load(f)

        self.reqs = [requests.get(i) for i in self.links]
        self.sources = [BeautifulSoup(req.content, 'html.parser') for req in self.reqs]

        self.prices = [Window.find_lowest_price(source, 'span', attrs={'class': 'prc-dsc'}) for source in self.sources]
        self.prices_og = [Window.find_lowest_price(source, 'span', attrs={'class': 'prc-org'}) for source in self.sources]
        self.target_prices = [v for k, v in self.targets.items()]
        self.h1 = [source.find('h1', attrs={'class': 'pr-new-br'}) for source in self.sources]

        self.labels = {}

        self.link_to_add = tk.StringVar()
        self.link_lbl = ttk.Label(self.root, text='Link')
        self.link_entry = ttk.Entry(self.root, textvariable=self.link_to_add, width=100)
        self.s1 = ttk.Separator(self.root, orient='horizontal')
        self.target = tk.DoubleVar()
        self.target_lbl = ttk.Label(self.root, text='Target Price (₺)')
        self.target_entry = ttk.Entry(self.root, textvariable=self.target)
        self.s2 = ttk.Separator(self.root, orient='horizontal')
        self.add_btn = ttk.Button(self.root, text='Add link', command=self.add_link)
        self.s3 = ttk.Separator(self.root, orient='horizontal')
        self.clear_targets = ttk.Button(self.root, text='Clear targets', command=self.clear_targets)
        self.s4 = ttk.Separator(self.root, orient='horizontal')
        self.fot_text = tk.StringVar(value='Enable force-overwrite target')
        self.fot_btn = ttk.Button(self.root, textvariable=self.fot_text, command=self.switch)
        self.s5 = ttk.Separator(self.root, orient='horizontal')

        self.link_lbl.pack()
        self.link_entry.pack()
        self.s1.pack(fill='x')
        self.target_lbl.pack()
        self.target_entry.pack()
        self.s2.pack(fill='x')
        self.add_btn.pack()
        self.s3.pack(fill='x')
        self.clear_targets.pack()
        self.s4.pack(fill='x')
        self.fot_btn.pack()
        self.s5.pack(fill='x')
        for label in self.labels.values():
            label.pack()

    def __call__(self):
        self.__init__()

    def add_link(self):
        self.links.append(self.link_to_add.get())
        self.link_to_add.set('')

        self.reqs = [requests.get(i) for i in self.links]
        self.sources = [BeautifulSoup(req.content, 'html.parser') for req in self.reqs]

        self.prices = [self.find_lowest_price(source, 'span', attrs={'class': 'prc-dsc'}) for source in self.sources]
        self.prices_og = [source.find('span', attrs={'class': 'prc-org'}) for source in self.sources]
        self.h1 = [source.find('h1', attrs={'class': 'pr-new-br'}) for source in self.sources]
        name = Window.removesurrounding(self.h1[-1].find('span').text, ' ')
        price: float

        try:
            if self.target_prices[-1] > self.target.get() > 0 or self.fot:
                raise IndexError
        except IndexError:
            self.target_prices.append(self.target.get())
            price = self.target_prices[-1]
            self.targets[name] = self.target.get()
        self.labels[name] = ttk.Label(self.root, text=('' if self.h1[-1].find('a') is None else self.h1[-1].find('a').text + ' - ') + Window.removesurrounding(self.h1[-1].find('span').text, ' ') + ' - ' + str(self.prices[-1]) + '₺' + ('' if self.prices_og[-1] is None else ' - Original price: ' + self.prices_og[-1].text.replace('.', '').replace(' TL', '₺') + f' ({round(100 * ((float(self.prices_og[-1].text.removesuffix(" TL").replace(".", "").replace(",", ".")) / self.prices[-1]) - 1), 2)}% discount)') + ' - ' + f'Target: {self.targets[name]}₺')

    def clear_targets(self):
        self.targets = {}
        self.target_prices = []

    def switch(self):
        if self.fot_text.get() == 'Enable force-overwrite target':
            self.fot_text.set('Disable force-overwrite target')

        else:
            self.fot_text.set('Enable force-overwrite target')

        self.fot = not self.fot

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

    def on_close(self):
        pop_quit = PopupOKCancel(self, 'Quit', 'Would you like to quit?', self.close)

    def launch(self):
        def pack_labels():
            print(self.labels)
            for label in self.labels.values():
                label.pack_forget()
                label.pack()

            for price in self.prices:
                for trpr in self.targets.items():
                    if trpr[1] >= price:
                        pop = PopupOK(self, 'Target reached', f'Target reached for {trpr[0]}!')
                        pop.show()

            self.root.after(1000, pack_labels)

        self.root.after(1000, pack_labels)
        self.root.mainloop()

    def close(self):
        with open('targets.json', 'w') as f:
            json.dump(self.targets, f)
        self.root.destroy()


if __name__ == '__main__':
    tp = Window()
    tp.launch()
