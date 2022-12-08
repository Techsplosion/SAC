import requests
import sqlite3
import tkinter as tk

from bs4 import BeautifulSoup
from tkinter import ttk


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
        self.targets = sqlite3.connect("targets.db")
        self.t_cur = self.targets.cursor()
        self.t_cur.execute("""CREATE TABLE IF NOT EXISTS targets(prod_name TEXT, prod_target FLOAT)""")

        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.fot = False  # force-overwrite the target

        self.links = []

        self.reqs = [requests.get(i) for i in self.links]
        self.sources = [BeautifulSoup(req.content, 'html.parser') for req in self.reqs]

        self.prices = [Window.find_lowest_price(source, 'span', attrs={'class': 'prc-dsc'}) for source in self.sources]
        self.prices_og = [Window.find_lowest_price(source, 'span', attrs={'class': 'prc-org'}) for source in self.sources]
        self.t_cur.execute('SELECT * FROM targets')
        self.target_prices = {elmt[0]: elmt[1] for elmt in self.t_cur.fetchall()}
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

        self.t_cur.execute('SELECT * FROM targets')
        self.target_prices = {elmt[0]: elmt[1] for elmt in self.t_cur.fetchall()}

        name = Window.removesurrounding(self.h1[-1].find('span').text, ' ')
        price: float

        try:
            if self.target_prices[name] > self.target.get() > 0 or self.fot:
                self.target_prices[name] = self.target.get()
                self.t_cur.execute(f'UPDATE targets SET prod_target = {self.target.get()} WHERE prod_name="{name}"')
        except KeyError:
            self.target_prices[name] = self.target.get()
            self.t_cur.execute(f'INSERT INTO targets VALUES("{name}", {self.target.get()})')

        self.labels[name] = ttk.Label(self.root, text=('' if self.h1[-1].find('a') is None else self.h1[-1].find('a').text + ' - ') + Window.removesurrounding(self.h1[-1].find('span').text, ' ') + ' - ' + str(self.prices[-1]) + '₺' + ('' if self.prices_og[-1] is None else ' - Original price: ' + self.prices_og[-1].text.replace('.', '').replace(' TL', '₺') + f' ({round(100 * ((float(self.prices_og[-1].text.removesuffix(" TL").replace(".", "").replace(",", ".")) / self.prices[-1]) - 1), 2)}% discount)') + ' - ' + f'Target: {self.target_prices[name]}₺')
        self.t_cur.execute('SELECT * FROM targets')

    def clear_targets(self):
        with open('targets.db', 'w') as f:
            f.write('')

        self.t_cur.execute("""CREATE TABLE IF NOT EXISTS targets(prod_name TEXT, prod_target FLOAT)""")
        self.target_prices = {}

    def switch(self):
        self.fot = not self.fot

        if self.fot:
            self.fot_text.set('Disable force-overwrite target')

        else:
            self.fot_text.set('Enable force-overwrite target')

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
        pop_quit = PopupOKCancel(self, 'Quit', 'Would you like to quit?', self.close)  # NOQA

    def launch(self):
        def pack_labels():
            for label in self.labels.values():
                label.pack_forget()
                label.pack()

            for price in self.prices:
                for trpr in self.target_prices.items():
                    if trpr[1] >= price:
                        pop = PopupOK(self, 'Target reached', f'Target reached for {trpr[0]}!')
                        pop.show()

            self.root.after(1000, pack_labels)

        self.root.after(1000, pack_labels)
        self.root.mainloop()

    def close(self):
        self.targets.commit()
        self.targets.close()
        self.root.destroy()


if __name__ == '__main__':
    tp = Window()
    tp.launch()
