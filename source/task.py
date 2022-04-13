from treelib import Tree
from copy import copy
from itertools import *
from sys import getsizeof
from datetime import datetime

from .utils import *


class Task:
    def __init__(self, **kwargs):
        self.step = kwargs['step']
        self.r = kwargs['r']
        self.days = tuple(kwargs['days'].values())
        self.prices = kwargs['prices']
        self.task_started_at = datetime.now()
        self.optimization = kwargs.get('optimization')

    def overload(self, count_of_workers: int, result: int, count: int):
        result += count * self.prices['c1']
        return count_of_workers, result, count

    def sleep(self, count_of_workers: int, result: int, count: int):
        result += count * self.prices['c2']
        return count_of_workers, result, count

    def hire(self, count_of_workers: int, result: int, count: int):
        result += count * self.prices['c3']
        count_of_workers += count
        return count_of_workers, result, count

    def unhire(self, count_of_workers: int, result: int, count: int):
        result += count * self.prices['c4']
        count_of_workers -= count
        return count_of_workers, result, count

    def __show(self, other: dict, day, total_nodes: int, day_started_at: datetime) -> None:
        print(' | '.join(
            [f'{item}: {other[item]} bytes' for item in list(
                other.keys())]) + f' | Day: {day} | Total nodes: {total_nodes} | Elapsed: {int((datetime.now() - day_started_at).total_seconds())} sec.',
              end='\r')

    def __verbose(self, items):
        items = [x.__name__ for x in items]
        verbose_view = []
        if 'overload' in items:
            c = items.count("overload")
            verbose_view.append(f'{c if c != 1 else ""}C1')
        if 'sleep' in items:
            c = items.count("sleep")
            verbose_view.append(f'{c if c != 1 else ""}C2')
        if 'hire' in items:
            c = items.count("hire")
            verbose_view.append(f'{c if c != 1 else ""}C3')
        if 'unhire' in items:
            c = items.count("unhire")
            verbose_view.append(f'{c if c != 1 else ""}C4')

        verbose_view = '+'.join(verbose_view)
        if not verbose_view:
            verbose_view = '</>'

        return verbose_view

    def __define_methods(self, count_of_workers: int, need_workers: int) -> list:
        methods = []

        if count_of_workers < need_workers:
            if count_of_workers > 0 and (
                    self.prices['c1'] < (self.prices['c3'] + self.prices['c4'])):  # if c1 have reason
                methods.append(self.overload)
            methods.append(self.hire)
        elif count_of_workers > need_workers:
            # if count_of_workers > 0 and (
            #         self.prices['c2'] < (self.prices['c3'] + self.prices['c4'])):  # if c2 have reason ?
            methods.append(self.sleep)
            methods.append(self.unhire)

        return methods

    def __is_similar(self, items) -> bool:
        return len(set(items)) == 1

    def __resolve_tries(self, delta: int, methods: list) -> list:
        tries = product(methods, repeat=delta)
        tries = [[y.__name__ for y in x] for x in tries]
        tries = [tuple(sorted(x)) for x in tries]
        tries = list(set(tries))
        if self.optimization:
            if self.optimization == 'similarity':
                tries = [x for x in tries if self.__is_similar(x)]
            elif self.optimization == 'rSimilarity':
                tries = [x for x in tries if not self.__is_similar(x)]

        tries = [[getattr(self, y) for y in x] for x in tries]

        return tries

    def calculate(self, days_up_to=8):
        tree = Tree()
        initial_cow = self.r
        tree.create_node(f"R: {initial_cow}", f'd0_0',
                         data={'cnt': initial_cow, 'price': 0})  # Day 0 or Root

        for di, day in enumerate(self.days):
            day_started_at = datetime.now()
            print()
            need_workers = day
            prev_day = f'd{di}'
            di += 1
            current_day = f'd{di}'

            if di == 1:
                methods = self.__define_methods(initial_cow, need_workers)
                delta = abs(initial_cow - need_workers)

                tries = self.__resolve_tries(delta, methods)

                for i, item in enumerate(tries):
                    tmp_res = 0
                    tmp_cow = copy(initial_cow)
                    for x in item:
                        tmp_cow, tmp_res, _ = x(tmp_cow, tmp_res, self.step)

                    verbose_view = self.__verbose(item)
                    tree.create_node(str(f'C:{tmp_cow}|P:{tmp_res}|V:{verbose_view}|N:d{1}_{i}|R:{need_workers}'),
                                     f'{current_day}_{i}',
                                     data={'cnt': tmp_cow, 'price': tmp_res, 'total_price': tmp_res,
                                           'vw': verbose_view}, parent='d0_0')

                    self.__show({'Tree': getsizeof(tree.nodes), 'Steps': getsizeof(tries)}, current_day,
                                len(tree.nodes), day_started_at)
            else:
                nodes_names = [x for x in tree.nodes if prev_day in x]
                epoch = 0
                for nd_i, nname in enumerate(nodes_names):
                    pnode = tree.get_node(nname)
                    pcnt = pnode.data['cnt']
                    ptotal_price = pnode.data['total_price']

                    delta = abs(pcnt - need_workers)
                    methods = self.__define_methods(pcnt, need_workers)

                    tries = self.__resolve_tries(delta, methods)

                    for i, item in enumerate(tries):
                        tmp_cow = copy(pcnt)
                        tmp_tp = copy(ptotal_price)

                        new_price = 0
                        for x in item:
                            tmp_cow, new_price, _ = x(tmp_cow, new_price, self.step)

                        verbose_view = self.__verbose(item)

                        tree.create_node(
                            str(f'C:{tmp_cow}|P:{new_price}|V:{verbose_view}|N:{current_day}_{epoch}|R:{need_workers}'),
                            f'{current_day}_{epoch}',
                            data={'cnt': tmp_cow, 'price': new_price, 'total_price': new_price + tmp_tp,
                                  'vw': verbose_view}, parent=nname)
                        epoch += 1

                        self.__show({'Tree': getsizeof(tree.nodes), 'Steps': getsizeof(tries)}, current_day,
                                    len(tree.nodes), day_started_at)
            if di == days_up_to:
                break

        print()
        print('Tree built. Resolving min path...')

        last_nodes = [x for x in tree.nodes if x.startswith(f'd{days_up_to}_')]
        vals = [tree.get_node(x).data['total_price'] for x in last_nodes]
        min_val = min(vals)
        min_name = last_nodes[vals.index(min_val)]
        node = tree.get_node(min_name)
        fullpath = [node.data['vw']]
        tmp = node
        while True:
            try:
                cur = tree.parent(tmp.identifier)
                fullpath.append(cur.data['vw'])
                tmp = cur
            except:
                break

        fullpath.reverse()

        print(f'Min price is: {min_val} | Tag: {f"({node.tag})"} | Name: {min_name} | FullPath={" + ".join(fullpath)}')
        print(f'Work done. Elapsed time: {int((datetime.now() - self.task_started_at).total_seconds())} sec.')

        if yes_no('Save to graphviz?'):
            tree.to_graphviz('result')

        # tree.show()
