from typing import Iterable, Optional, TextIO
import time

from state_representation import *

# din laboratoare
class NodParcurgere:
    '''Un nod din arborele de parcurgere.'''
    def __init__(self, state: State, parinte: 'NodParcurgere',
            g: Optional[int] = 0, h: Optional[int] = 0, cost: Optional[int] = 0):
        '''
        Args:
            state: Starea pentru care este facut nodul.
            parinte: Nodul care precede nodul curent in arborele de cautare.
            g: Costul drumului de la origine la nodul curent.
            h: Costul estimat al drumului de la nodul curent la o stare finala.
            cost: Costul muchiei de la nodul parinte la nodul curent.
        '''
        self.state = state
        self.parinte = parinte #parintele din arborele de parcurgere
        self.g = g
        self.h = h
        self.f = self.g+self.h
        self.cost = cost

    def obtine_drum(self) -> Iterable['NodParcurgere']:
        '''Obtine drumul de la origine la nodul curent.'''
        l=[self];
        nod=self
        while nod.parinte is not None:
            l.insert(0, nod.parinte)
            nod=nod.parinte
        return l

    def afisare_drum(self, f: TextIO, start_time: float) -> None:
        '''Afiseaza drumul la stdout si in fisierul f.
        
        Args:
            f: Fisierul in care sa fie scris drumul.
            start_time: Timpul la care a inceput cautarea acestei solutii.'''
        time_delta = time.time() - start_time
        # print('Timpul pentru gasirea solutiei:', time_delta)
        f.write('Timpul pentru gasirea solutiei:' + str(time_delta) + '\n')

        drum = self.obtine_drum()

        cost_drum = 0
        for nod in drum:
            cost_drum += nod.cost

        # print('Lungimea drumului:', len(drum))
        f.write('Lungimea drumului: ' + str(len(drum)) + '\n')
        f.write('Costul drumului:' + str(cost_drum) + '\n')

        for index_nod, nod in enumerate(drum):
            # print(str(index_nod+1) + ')')
            # print(nod.state.to_string())
            f.write(str(index_nod+1) + ')\n')
            f.write('g = ' + str(nod.g) + '\n')
            f.write('h = ' + str(nod.h) + '\n')
            f.write(nod.state.to_string() + '\n')
        # print(16 * len(self.state.s) * '_')
        f.write(16 * len(self.state.s) * '_' + '\n')


    def calculeaza_h(self, state: State, tip_euristica: str = 'euristica_banala'):
        '''
        Calculeaza distanta estimata a drumului de la starea curenta la o stare finala.
        'euristica_banala' - Returneaza 1 daca starea curenta nu este una finala, 0 daca este.
        'euristica_admisibila_1' - Calculeaza numarul minim de stive de pe care trebuie scoase blocuri
            ca sa se ajunga la o stare finala.
        'euristica_admisibila_2' - Calculeaza suma minima a greutatilor blocurilor care trebuie mutate
            (ignorand rezistentele) ca sa se ajunga la o stare finala.
        'euristica_neadmisibila' - Calculeaza suma greutatilor unor blocuri care trebuie mutate ca sa
            se ajunga la o stare finala. Obs: Suma nu este minima.
        Args:
            state (State): Starea de la care se calculeaza distanta.
            tip_euristica (str): 'euristica_banala', 'euristica_admisibila_1', 'euristica_admisibila_2',
                orice altceva este o euristica neadmisibila.
        '''
        if tip_euristica == 'euristica_banala':
            if not state.is_end_state():
                return 1
            return 0
        elif tip_euristica == 'euristica_admisibila_1':
            # Numarul de stive de pe care trebuie scoase blocuri
            num_blocuri = sum([stiva.get_height() for stiva in state.s])
            n = num_blocuri // len(state.s)
            m = num_blocuri % len(state.s)

            # Cate blocuri trebuie mutate ca toate stivele sa aiba H >= n
            blocuri_lipsa = 0
            for stiva in state.s:
                blocuri_lipsa += max(0, n-stiva.get_height())

            cost = 0
            for stiva in state.s:
                if stiva.get_height() > n+1:
                    cost += 1
                    blocuri_lipsa -= (stiva.get_height() - (n+1))

            cost += max(0, blocuri_lipsa-cost)

            return cost
        elif tip_euristica == 'euristica_admisibila_2':
            # 1) ne asiguram ca nu raman stive cu H > n+1
            # 2) Daca numarul de stive cu H == n+1 e mai mare decat num_blocuri % num_stive
            #    adun costurile blocurilor cu greutatile cele mai mici
            num_blocuri = sum([stiva.get_height() for stiva in state.s])
            n = num_blocuri // len(state.s)
            m = num_blocuri % len(state.s)

            cost = 0
            border_size = 0
            border_costs = []

            for stiva in state.s:
                # add costs of obvious blocks
                for i in range(n+1, stiva.get_height()):
                    cost += stiva[i].greutate
                if stiva.get_height() >= n+1:
                    border_size += 1
                    border_costs.append(stiva[n].greutate)

            if border_size > m:
                border_costs.sort()
                for i in range(border_size-m):
                    cost += border_costs[i]

            return cost
        else:
            # Euristica admisibila 2, dar fara conditia referitoare la blocurile cu H = n+1
            num_blocuri = sum([stiva.get_height() for stiva in state.s])
            n = num_blocuri // len(state.s)
            m = num_blocuri % len(state.s)

            cost = 0
            border_size = 0
            border_costs = []

            for stiva in state.s:
                # add costs of obvious blocks
                for i in range(n+1, stiva.get_height()):
                    cost += stiva[i].greutate
                if stiva.get_height() >= n+1:
                    border_size += 1
                    border_costs.append(stiva[n].greutate)
            
            if border_size > m:
                # Obs: nu se mai face sortarea.
                # Conditia ca h'(nod) <= h(nod) nu mai este indeplinita mereu.
                for i in range(border_size-m):
                    cost += border_costs[i]
            return cost


    def generate_successors(self, euristica: str ='euristica_banala') -> Iterable['NodParcurgere']:
        '''
        Genereaza succesorii nodului curent.
        Args:
            tip_euristica: 'euristica_banala', 'euristica_admisibila_1', 'euristica_admisibila_2',
                orice altceva este o euristica neadmisibila.
        '''
        successors = []
        state_successors, costs = self.state.generate_successors()
        for state_successor, cost in zip(state_successors, costs):
            h = self.calculeaza_h(state_successor, euristica)
            successors.append(NodParcurgere(state_successor, self, cost+self.g, h, cost))
        return successors

    def is_end_state(self):
        return self.state.is_end_state()


class Graf:
    '''Clasa care retine informatiile despre starea nodurilor din graf in timpul unei parcurgeri.
    
    Attributes:
        start: Starea de la care se va incepe fiecare parcurgere a grafului.
        discovered: Set care contine nodurile descoperite in parcurgere.
        processed: Set care contine nodurile procesate in parcurgere.
    '''
    def __init__(self, start: State):
        '''
        Args:
            start: Starea de la care se va incepe fiecare parcurgere a grafului.
        '''
        self.start = start
        self.discovered = set()
        self.processed = set()

    def set_discovered(self, state: State):
        self.discovered.add(state)

    def is_discovered(self, state: State) -> bool:
        return state in self.discovered

    def set_processed(self, state: State):
        self.processed.add(state)
    
    def is_processed(self, state: State) -> bool:
        return state in self.processed

    def reset(self):
        '''Sterge toate informatiile despre procesarea si descoperirea nodurilor.'''
        self.discovered.clear()
        self.processed.clear()