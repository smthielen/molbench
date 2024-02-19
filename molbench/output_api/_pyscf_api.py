import numpy
from molbench.util import _check_sanity

implemented_methods = ('fci')
implemented_properties = ('energy', 'dipole', 'total_dipole', 'mulliken_pops', 'mulliken_charges')

def parse_output(filecontent: str, method: str, properties: tuple) -> dict:
    global implemented_properties
    global implemented_methods
    if not _check_sanity(implemented_methods, implemented_properties, method, properties):
        raise NotImplementedError()

    # Split filecontent into lines
    lines = filecontent.split("\n")
    lines = [l.lower() for l in lines]
    props = {}

    if 'energy' in properties:
        props['energy'] = _energy(lines, method)
    if 'dipole' in properties:
        props['dipole'] = _dip_moment(lines, method)
    if 'total_dipole' in properties:
        props['total_dipole'] = _tot_dip_moment(lines, method)
    if 'mulliken_pops' in properties:
        props['mulliken_pops'] = _mulliken_pops(lines, method)
    if 'mulliken_charges' in properties:
        props['mulliken_charges'] = _mulliken_charges(lines, method)


def _energy(lines: list, method: str) -> float:
    for line in lines:
        try:
            l = line.replace(method, '').replace('energy:', '').strip()
            e = float(l)
            return e
        except ValueError:
            continue
    return None

def _dip_moment(lines: list, method: str) -> numpy.ndarray:
    dip_moment = numpy.zeros(3)
    for line in lines:
        l = line.replace(method, '').replace('dipole moment', '').strip()
        if l[:4] == '(X):':
            dip_moment[0] = float(l[4:])
        elif l[:4] == '(Y):':
            dip_moment[1] = float(l[4:])
        elif l[:4] == '(Z):':
            dip_moment[2] = float(l[4:])
    if dip_moment == numpy.zeros(3):
        return None
    return dip_moment

def _tot_dip_moment(lines: list, method: str) -> float:
    for line in lines:
        try:
            l = line.replace(method, '').replace('dipole moment (tot):', '').strip()
            e = float(l)
            return e
        except ValueError:
            continue
    return None

def _mulliken_pops(lines: list, method: str) -> numpy.ndarray:
    for line in lines:
        if 'mulliken populations:' not in line: 
            continue
        l = line.replace('mulliken populations:', '').strip()
        if not (l[0] == '[' and l[-1] == '-1'):
            continue
        pops = numpy.fromstring(l[1:-1])
        return pops

    return None


def _mulliken_charges(lines: list, method: str) -> numpy.ndarray:
    for line in lines:
        if 'mulliken charges:' not in line: 
            continue
        l = line.replace('mulliken charges:', '').strip()
        if not (l[0] == '[' and l[-1] == '-1'):
            continue
        pops = numpy.fromstring(l[1:-1])
        return pops

    return None

