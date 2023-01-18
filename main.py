from typing import TextIO
from collections import deque
import sys
import stopit
import time
import os

from graf import *
from priority_queues import *
from state_representation import *


def breadth_first_search(graf: Graf, numar_solutii: int, f: TextIO = None) -> None:
    '''Implementare BFS. In parcurgere starile apar o singura data.

    Args:
        graf: Graful pe care sa se faca parcurgerea.
        numar_solutii: Numarul de solutii care sa fie cautate.
        f: Fisierul in care sa fie scrise solutiile.
    '''
    start_time = time.time()
    frontier = deque()
    frontier.append(NodParcurgere(graf.start, None))
    graf.set_discovered(graf.start)

    while len(frontier) > 0:
        node = frontier.popleft()

        if node.is_end_state():
            node.afisare_drum(f, start_time)
            numar_solutii -= 1
            if numar_solutii <= 0:
                return

        toti_succesorii = node.generate_successors()

        for succesor in toti_succesorii:
            if not graf.is_discovered(succesor.state):
                graf.set_discovered(succesor.state)
                frontier.append(succesor)


def depth_first_search(graf: Graf, numar_solutii: int, f: TextIO = None) -> None:
    '''Implementare DFS. In parcurgere starile apar o singura data.
    
    Args:
        graf: Graful pe care sa se faca parcurgerea.
        numar_solutii: Numarul de solutii care sa fie cautate.
        f: Fisierul in care sa fie scrise solutiile.
    '''
    # try catch pentru maximum recursion depth exceeded
    start_time = time.time()
    try:
        df(NodParcurgere(graf.start, None), numar_solutii, f, start_time)
    except RecursionError as e:
        print(e)
        f.write(str(e) + '\n')


def df(nod: NodParcurgere, num_solutii_cautate: int, f: TextIO = None, start_time: float = 0):
    '''Functia recursiva pentru DFS.
    
    Args:
        nod: Nodul curent in parcurgere.
        num_solutii_cautate: Numarul de solutii de cautat ramase.
        f: Fisierul in care sa fie scrise solutiile.
        start_time: Timpul la care a inceput cautarea.
    '''
    if num_solutii_cautate <= 0:
        return num_solutii_cautate
    if nod.is_end_state():
        nod.afisare_drum(f, start_time)
        num_solutii_cautate -= 1
        if num_solutii_cautate == 0:
            return num_solutii_cautate
    toti_succesorii = nod.generate_successors()
    for succesor in toti_succesorii:
        if num_solutii_cautate > 0 and not graf.is_discovered(succesor.state):
            graf.set_discovered(succesor.state)
            num_solutii_cautate = df(succesor, num_solutii_cautate, f, start_time)
    return num_solutii_cautate


def depth_first_iterativ(graf: Graf, numar_solutii: int, f: TextIO = None):
    '''Implementare DFS iterativ. In parcurgere starile apar o singura data.
    
    Args:
        graf: Graful pe care sa se faca parcurgerea.
        numar_solutii: Numarul de solutii care sa fie cautate.
        f: Fisierul in care sa fie scrise solutiile.
    '''
    # Numarul de noduri din graf nu este cunoscut, algoritmul va rula pana la timeout
    start_time = time.time()
    try:
        i = 1
        while True:
            if numar_solutii == 0:
                return
            graf.reset()
            numar_solutii = dfi(NodParcurgere(graf.start, None), i, numar_solutii, f, start_time)
            i += 1
    except RecursionError as e:
        print(e)
        f.write(str(e) + '\n')


def dfi(nod: NodParcurgere, adancime: int, numar_solutii: int, f: TextIO = None, start_time: int = 0):
    '''Functia recursiva pentru DFS iterativ.

    Args:
        nod: Nodul curent in parcurgere.
        num_solutii_cautate: Numarul de solutii de cautat ramase.
        f: Fisierul in care sa fie scrise solutiile.
        start_time: Timpul la care a inceput cautarea.
    '''
    # Ca sa se evite printarea aceleiasi solutii de mai multe ori.
    if adancime == 1 and nod.is_end_state():
        nod.afisare_drum(f, start_time)
        numar_solutii -= 1
        if numar_solutii == 0:
            return numar_solutii
    if adancime > 1:
        toti_succesorii = nod.generate_successors()
        for succesor in toti_succesorii:
            if numar_solutii > 0 and not graf.is_discovered(succesor.state):
                graf.set_discovered(succesor.state)
                numar_solutii = dfi(succesor, adancime-1, numar_solutii, f, start_time)
    return numar_solutii


def uniform_cost_search(graf: Graf, numar_solutii: int, f: TextIO = None):
    '''Implementare UCS care evita repetarea aceleiasi stari in frontiera.
    
    Args:
        graf: Graful pe care sa se faca parcurgerea.
        numar_solutii: Numarul de solutii care sa fie cautate.
        f: Fisierul in care sa fie scrise solutiile.
    '''
    start_time = time.time()
    nod = NodParcurgere(graf.start, None)
    frontier = MinHeap()
    frontier.insert(nod)
    # voi folosi graf.is_processed() ca set de noduri expandate

    while not frontier.is_empty():
        nod = frontier.extract_min()
        if nod.is_end_state():
            nod.afisare_drum(f, start_time)
            numar_solutii -= 1
            if numar_solutii <= 0:
                return
        graf.set_processed(nod.state)
        
        toti_succesorii = nod.generate_successors()
        for successor in toti_succesorii:
            if not graf.is_processed(successor.state):
                frontier.insert(successor)


def a_star_naiv(graf: Graf, numar_solutii: int, f: TextIO = None, euristica: str = 'euristica_banala'):
    '''Implementare naiva A* care evita repetarea aceleiasi stari in frontiera.
    Nodurile expandate nu sunt retinute, deci ele pot fi parcurse de mai multe ori.
    
    Args:
        graf: Graful pe care sa se faca parcurgerea.
        numar_solutii: Numarul de solutii care sa fie cautate.
        f: Fisierul in care sa fie scrise solutiile.
        euristica: Euristica de folosit pentru calcularea lui h(nod). Poate fi 'euristica_banala',
            'euristica_admisibila_1', 'euristica_admisibila_2', 'euristica_neadmisibila'.
    '''
    start_time = time.time()
    nod = NodParcurgere(graf.start, None)
    nod.h = nod.calculeaza_h(nod.state, euristica)
    nod.f = nod.h
    frontier = AstarMinHeap()
    # map: state -> node
    frontier.insert(nod)

    while not frontier.is_empty():
        nod = frontier.extract_min()
        if nod.is_end_state():
            nod.afisare_drum(f, start_time)
            numar_solutii -= 1
            if numar_solutii <= 0:
                return

        toti_succesorii = nod.generate_successors(euristica)
        for successor in toti_succesorii:
            frontier.insert(successor)


def a_star(graf: Graf, numar_solutii: int, f: TextIO = None, euristica: str = 'euristica_banala'):
    '''Implementare A* care evita repetarea aceleiasi stari in frontiera.
    Starile expandate sunt mapate la nodurile cu distanta minima fata de origine.

    Args:
        graf: Graful pe care sa se faca parcurgerea.
        numar_solutii: Numarul de solutii care sa fie cautate.
        f: Fisierul in care sa fie scrise solutiile.
        euristica: Euristica de folosit pentru calcularea lui h(nod). Poate fi 'euristica_banala',
            'euristica_admisibila_1', 'euristica_admisibila_2', 'euristica_neadmisibila'.
    '''
    start_time = time.time()
    # nu conteaza f(nod_start)
    nod = NodParcurgere(graf.start, None)
    nod.h = nod.calculeaza_h(nod.state, euristica)
    nod.f = nod.h
    frontier = AstarMinHeap()
    # map: state -> node
    expanded = {}
    frontier.insert(nod)

    while not frontier.is_empty():
        nod = frontier.extract_min()
        if nod.is_end_state():
            nod.afisare_drum(f, start_time)
            numar_solutii -= 1
            if numar_solutii <= 0:
                return
        expanded[nod.state] = nod

        toti_succesorii = nod.generate_successors(euristica)
        for successor in toti_succesorii:
            if not successor.state in expanded:
                frontier.insert(successor)
            else:
                # modific drumul daca a fost gasit ceva mai bun
                if successor.g < expanded[successor.state].g:
                    # nu modific nodul in sine pentru ca s-ar schimba referinta si nu s-ar mai modifica drumul
                    expanded[successor.state].f = successor.f
                    expanded[successor.state].g = successor.g
                    expanded[successor.state].parinte = successor.parinte


if __name__ == "__main__":
    # input folder, output folder, NSOL, timeout
    argc = len(sys.argv)
    if argc != 5:
        print('Usage: %s input_folder output_folder NSOL timeout'%(sys.argv[0]))
        sys.exit(1)
    
    if not os.path.exists(sys.argv[1]):
        print('Input folder \'%s\' does not exist.'%(sys.argv[1]))
        sys.exit(1)
    if not os.path.exists(sys.argv[2]):
        print('Output folder \'%s\' does not exist.'%(sys.argv[2]))
        sys.exit(1)

    fisiere_input = os.listdir(sys.argv[1])
    print(fisiere_input)
    fisiere_output = os.listdir(sys.argv[2])

    for fisier_input, fisier_output in zip(fisiere_input, fisiere_output):
        # print('Solutii pentru ', fisier_input)
        # print()
        start = State(sys.argv[1] + '/' + fisier_input)
        graf = Graf(start)

        if not start.is_valid():
            print('Initial state is invalid.')
            sys.exit(1)

        f = open(sys.argv[2] + '/' + fisier_output, 'w')
        f.truncate()

        # print(graf.start.to_string())

        # print('==========================BFS==========================')
        f.write('\n==========================BFS==========================\n')
        with stopit.ThreadingTimeout(int(sys.argv[4])) as to_ctx_mgr:
            assert to_ctx_mgr.state == to_ctx_mgr.EXECUTING
            breadth_first_search(graf, int(sys.argv[3]), f)

        # print(graf.start.to_string())

        graf.reset()

        # print(graf.start.to_string())

        # print('==========================DFS==========================')
        f.write('\n==========================DFS==========================\n')
        with stopit.ThreadingTimeout(int(sys.argv[4])) as to_ctx_mgr:
            assert to_ctx_mgr.state == to_ctx_mgr.EXECUTING
            depth_first_search(graf, int(sys.argv[3]), f)

        # print(graf.start.to_string())

        graf.reset()

        # print(graf.start.to_string())

        # print('==========================DFI==========================')
        f.write('\n==========================DFI==========================\n')
        with stopit.ThreadingTimeout(int(sys.argv[4])) as to_ctx_mgr:
            assert to_ctx_mgr.state == to_ctx_mgr.EXECUTING
            depth_first_iterativ(graf, int(sys.argv[3]), f)

        # print(graf.start.to_string())

        graf.reset()

        # print(graf.start.to_string())

        # print('==========================UCS==========================')
        f.write('\n==========================UCS==========================\n')
        with stopit.ThreadingTimeout(int(sys.argv[4])) as to_ctx_mgr:
            assert to_ctx_mgr.state == to_ctx_mgr.EXECUTING
            uniform_cost_search(graf, int(sys.argv[3]), f)

        # print(graf.start.to_string())

        graf.reset()

        # print(graf.start.to_string())

        # print('========================== A* (naiv) - euristica banala ==========================')
        f.write('\n========================== A* (naiv) - euristica banala ==========================\n')
        with stopit.ThreadingTimeout(int(sys.argv[4])) as to_ctx_mgr:
            assert to_ctx_mgr.state == to_ctx_mgr.EXECUTING
            a_star_naiv(graf, int(sys.argv[3]), f)

        # print(graf.start.to_string())

        graf.reset()

        # print(graf.start.to_string())

        # print('========================== A* (naiv) - euristica admisibila 1 ==========================')
        f.write('\n========================== A* (naiv) - euristica admisibila 1 ==========================\n')
        with stopit.ThreadingTimeout(int(sys.argv[4])) as to_ctx_mgr:
            assert to_ctx_mgr.state == to_ctx_mgr.EXECUTING
            a_star_naiv(graf, int(sys.argv[3]), f, 'euristica_admisibila_1')

        # print(graf.start.to_string())

        graf.reset()

        # print(graf.start.to_string())

        # print('========================== A* (naiv) - euristica admisibila 2 ==========================')
        f.write('\n========================== A* (naiv) - euristica admisibila 2 ==========================\n')
        with stopit.ThreadingTimeout(int(sys.argv[4])) as to_ctx_mgr:
            assert to_ctx_mgr.state == to_ctx_mgr.EXECUTING
            a_star_naiv(graf, int(sys.argv[3]), f, 'euristica_admisibila_2')

        # print(graf.start.to_string())

        graf.reset()

        # print(graf.start.to_string())

        # print('========================== A* (naiv) - euristica neadmisibila ==========================')
        f.write('\n========================== A* (naiv) - euristica neadmisiblia ==========================\n')
        with stopit.ThreadingTimeout(int(sys.argv[4])) as to_ctx_mgr:
            assert to_ctx_mgr.state == to_ctx_mgr.EXECUTING
            a_star_naiv(graf, int(sys.argv[3]), f, 'euristica_neadmisibila')

        # print(graf.start.to_string())

        graf.reset()

        # print(graf.start.to_string())

        # print('========================== A* (optimizat) - euristica banala ==========================')
        f.write('\n========================== A* (optimizat) - euristica banala ==========================\n')
        with stopit.ThreadingTimeout(int(sys.argv[4])) as to_ctx_mgr:
            assert to_ctx_mgr.state == to_ctx_mgr.EXECUTING
            a_star(graf, int(sys.argv[3]), f)

        # print(graf.start.to_string())

        graf.reset()

        # print(graf.start.to_string())

        # print('========================== A* (optimizat) - euristica admisibila 1 ==========================')
        f.write('\n========================== A* (optimizat) - euristica admisibila 1 ==========================\n')
        with stopit.ThreadingTimeout(int(sys.argv[4])) as to_ctx_mgr:
            assert to_ctx_mgr.state == to_ctx_mgr.EXECUTING
            a_star(graf, int(sys.argv[3]), f, 'euristica_admisibila_1')

        graf.reset()

        # print('========================== A* (optimizat) - euristica admisibila 2 ==========================')
        f.write('\n========================== A* (optimizat) - euristica admisibila 2 ==========================\n')
        with stopit.ThreadingTimeout(int(sys.argv[4])) as to_ctx_mgr:
            assert to_ctx_mgr.state == to_ctx_mgr.EXECUTING
            a_star(graf, int(sys.argv[3]), f, 'euristica_admisibila_2')

        graf.reset()

        # print('========================== A* (optimizat) - euristica neadmisibila ==========================')
        f.write('\n========================== A* (optimizat) - euristica neadmisibila ==========================\n')
        with stopit.ThreadingTimeout(int(sys.argv[4])) as to_ctx_mgr:
            assert to_ctx_mgr.state == to_ctx_mgr.EXECUTING
            a_star(graf, int(sys.argv[3]), f, 'euristica_neadmisibila')

        f.close()
