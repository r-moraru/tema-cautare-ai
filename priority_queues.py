from sbbst import sbbst

from state_representation import *
from graf import *


class MinHeapKey:
    '''Cheie utilizata in PQ-ul pentru UCS.

    Attributes:
        nod: Nodul reprezentat de cheie.
    '''
    def __init__(self, nod: NodParcurgere):
        '''
        Args:
            nod: Nodul reprezentat de chieie.
        '''
        self.nod = nod
    
    def __lt__(self, other):
        '''Cheile se compara dupa distanta nodurilor lor fata de origine. Daca distanta e egala,
            se compara starile lexicografic, dupa reprezentarea lor sub forma de stringuri.'''
        if self.nod.g == other.nod.g:
            return str(self.nod.state) < str(other.nod.state)
        return self.nod.g < other.nod.g
    
    def __eq__(self, other):
        return self.nod.g == other.nod.g and str(self.nod.state) == str(other.nod.state)

    def __str__(self):
        return str(self.nod.state)


class AstarMinHeapKey:
    '''Cheie utilizata in PQ-ul pentru A*.

    Attributes:
        nod: Nodul reprezentat de cheie.
    '''
    def __init__(self, nod):
        '''
        Args:
            nod: Nodul reprezentat de chieie.
        '''
        self.nod = nod

    def __lt__(self, other):
        '''Cheile se compara dupa distanta estimata a drumului de la origine la o stare finala,
            trecand prin nodul reprezentat de chieie. Daca distanta e egala, se compara
            starile lexicografic, dupa reprezentarea lor sub forma de stringuri.'''
        if self.nod.f == other.nod.f:
            return str(self.nod.state) < str(other.nod.state)
        return self.nod.f < other.nod.f

    def __eq__(self, other):
        return self.nod.f == other.nod.f and str(self.nod.state) == str(other.nod.state)

    def __str__(self):
        return str(self.nod.state)


class MinHeap:
    '''Priority queue folosit pentru UCS.
    
    Format dintr-un arbore binar de cautare balansat si un dictionar
        care mapeaza starile la distanta minima de origine.
    Nodurile se sorteaza dupa distanta lor fata de origine.
    Inserarea, updatarea si stergerea oricarui nod pot fi facute in O(logN).

    Attributes:
        bt: arbore binar de cautare balansat care joaca rolul unui PQ.
        state_distances: Dictionar care mapeaza starile la distanta minima de origine.
            Utilizat pentru cautarea rapida in arborele binar a oricarei stari si pentru
            verificarea existentei oricarei stari in PQ.
    '''
    def __init__(self):
        self.bt = sbbst()
        self.state_distances = {}

    def extract_min(self) -> NodParcurgere:
        '''Scoate cel mai apropiat nod de origine din priority queue si il returneaza.
        
        Returns:
            Nodul cu cheie minima.
        '''
        nod = self.bt.getMinVal().nod
        self.bt.delete(MinHeapKey(nod))
        self.state_distances.pop(nod.state)
        return nod

    def is_empty(self) -> bool:
        '''Verifica daca numarul de noduri din PQ este 0.'''
        return len(self.state_distances) == 0

    def insert(self, nod: NodParcurgere) -> None:
        '''
        Insereaza nodul in priority queue.
        Daca starea exista deja in priority queue cu o distanta mai mare de origine,
        nodul starii este updatat.
        '''
        # daca deja exista state-ul, vad daca trebuie updatat
        if nod.state in self.state_distances:
            # if data in tree is outdated:
            if self.state_distances[nod.state] > nod.g:
                # remove old node
                old_node = NodParcurgere(nod.state, None, self.state_distances[nod.state])
                self.bt.delete(MinHeapKey(old_node))

                # insert updated data
                self.state_distances[nod.state] = nod.g
                self.bt.insert(MinHeapKey(nod))
        else:
            self.state_distances[nod.state] = nod.g
            self.bt.insert(MinHeapKey(nod))


class AstarMinHeap:
    '''Priority queue folosit pentru A*.
    Format dintr-un arbore binar de cautare balansat si un dictionar
        care mapeaza starile la f(nod_curent), distanta estimata a drumului origine -> nod_curent -> stare_finala.
    Nodurile se sorteaza dupa f(nod_curent).
    Inserarea, updatarea si stergerea oricarui nod pot fi facute in O(logN).
    '''
    def __init__(self):
        self.bt = sbbst()
        self.origin_distances = {}
        self.estimated_distances = {}

    def extract_min(self) -> NodParcurgere:
        '''
        Scoate nodul cu f(nod) minim din priority queue si il returneaza.
        '''
        nod = self.bt.getMinVal().nod
        self.bt.delete(AstarMinHeapKey(nod))
        self.origin_distances.pop(nod.state)
        self.estimated_distances.pop(nod.state)
        return nod

    def is_empty(self) -> bool:
        return len(self.origin_distances) == 0

    def insert(self, nod: NodParcurgere):
        '''
        Insereaza nodul in priority queue.
        Daca starea exista deja in priority queue cu f(nod_vechi) mai mare decat f(nod_nou),
        nodul starii este updatat.
        '''
        # daca deja exista state-ul, vad daca trebuie updatat
        if nod.state in self.origin_distances:
            # if data in tree is outdated:
            old_g = self.origin_distances[nod.state]
            old_h = self.estimated_distances[nod.state]
            old_f = old_g + old_h
            if (
                old_f > nod.f or
                (old_f == nod.f and old_g > nod.g)
            ):
                # remove old node
                old_node = NodParcurgere(nod.state, None, old_g, old_h)
                self.bt.delete(AstarMinHeapKey(old_node))

                # insert updated data
                self.origin_distances[nod.state] = nod.g
                self.estimated_distances[nod.state] = nod.h
                self.bt.insert(AstarMinHeapKey(nod))
        else:
            self.origin_distances[nod.state] = nod.g
            self.estimated_distances[nod.state] = nod.h
            self.bt.insert(AstarMinHeapKey(nod))
