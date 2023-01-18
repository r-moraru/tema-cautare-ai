from typing import Iterable
import copy


class Bloc:
    '''
    Informatiile despre un bloc.
    '''
    def __init__(self, nume: str, greutate: int, rezistenta: int):
        '''Bloc cu nume, greutate si rezistenta.
        
        Args:
            nume: Numele asociat blocului.
            greutate: Greutatea blocului.
            rezistenta: Greutatea maxima care poate fi pusa pe bloc.
        '''
        self.nume = nume
        self.greutate = greutate
        self.rezistenta = rezistenta
    
    def to_string(self) -> str:
        '''Folosita pentru output.'''
        return '[' + self.nume + '/' + str(self.greutate) + '/' + str(self.rezistenta) + ']'
    
    def __str__(self) -> str:
        '''Folosita pentru hashing.'''
        return '[' + self.nume + '/' + str(self.greutate) + '/' + str(self.rezistenta) + ']'


class Stiva:
    '''
    Stiva de blocuri.
    '''
    def __init__(self, string: str):
        '''Constructorul unei stive pornind de la un string.

        Args:
            string: Lista de blocuri sub forma de string (ex: c,3,10|a,5,14|g,2,8
                sau _ pentru stiva goala.)
        
        '''
        self.s = []
        string = string.strip()
        if string == '_':
            return

        blocuri = string.split('|')
        for bloc in blocuri:
            bloc_data = bloc.split(',')
            try:
                self.s.append(Bloc(bloc_data[0], int(bloc_data[1]), int(bloc_data[2])))
            except Exception as e:
                print('Failed to read block.')
                print(e)

    def is_valid(self) -> bool:
        '''Verifica daca exista blocuri cu rezistenta depasita in stiva.'''
        weight_sum = 0
        for bloc in reversed(self.s):
            if weight_sum > bloc.rezistenta:
                return False
            weight_sum += bloc.greutate
        return True

    def get_height(self) -> int:
        '''Numarul de blocuri din stiva.'''
        return len(self.s)

    def __getitem__(self, key: int) -> Bloc:
        return self.s[key]

    def __str__(self) -> str:
        '''Folosita pentru hashing.'''
        string = ''
        if len(self.s) == 0:
            string = '_'
            return string
        for bloc in self.s:
            string += bloc.nume + ','
        return string


class State:
    '''Reprezinta o stare a tuturor stivelor.'''
    def __init__(self, filepath: str):
        '''Constructorul unei stari citite dintr-un fisier.
        
        Args:
            filepath: Fisierul care contine descrierea starii,
                cate o stiva pe fiecare linie.
        '''
        self.s = []
        with open(filepath, 'r') as f:
            for line in f:
                stiva = Stiva(line)
                self.s.append(stiva)

    def generate_successors(self) -> Iterable['State']:
        '''Genereaza toate starile valide care pot urma starea curenta.'''
        states = []
        costs = []
        for stiva in self.s:
            if len(stiva.s) == 0:
                continue
            bloc = stiva.s.pop()
            for stiva_ad in self.s:
                if stiva_ad == stiva:
                    continue
                stiva_ad.s.append(bloc)
                if stiva_ad.is_valid():
                    states.append(copy.deepcopy(self))
                    costs.append(bloc.greutate)
                stiva_ad.s.pop()

            stiva.s.append(bloc)

        return states, costs

    def is_valid(self) -> bool:
        '''Verifica daca in starea curenta exista blocuri bloc cu rezistenta depasita.'''
        for stiva in self.s:
            if not stiva.is_valid():
                return False
        return True

    def to_string(self) -> str:
        '''Folosit pentru output.'''
        string = ''
        max_height = max([stiva.get_height() for stiva in self.s]) - 1
        max_block_len = 0
        for stiva in self.s:
            for block in stiva.s:
                max_block_len = max(max_block_len, len(block.to_string()))

        for height in range(max_height, -1, -1):
            for stiva in self.s:
                if stiva.get_height() > height:
                    string += stiva[height].to_string()
                    string += ' ' * (max_block_len - len(stiva[height].to_string()))
                else:
                    string += ' ' * max_block_len
                string += '\t'
            string += '\n'
        return string

    def is_end_state(self) -> bool:
        '''Verifica daca este o stare finala.'''
        num_blocuri = sum([stiva.get_height() for stiva in self.s])
        n = num_blocuri // len(self.s)
        border_size = 0

        # E suficient ca cel putin o stiva sa aiba H < n
        for stiva in self.s:
            if stiva.get_height() < n or stiva.get_height() > n+1:
                return False

        return True

    def __str__(self) -> str:
        '''Folosit pentru hashing.'''
        string = ''
        for stiva in self.s:
            string += str(stiva)
            string += '|'
        return string

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)