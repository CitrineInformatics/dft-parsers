from ..core import BlockParser
from builtins import super

def _parse_lattice_parameter(line, lines):
    return {"lattice parameter": float(line.split()[4])}

def _parse_header(line, lines):
    toks = line.split()
    return {
        "version": toks[2].lstrip("v."),
        "start_date": toks[5]
    }

def _parse_xc(line, lines):
    return {"exchange-correlation": line.partition("=")[2].partition("(")[0].split()}

def _parse_cutoff(line, lines):
    return {
        'kinetic-energy cutoff': float(line.split()[3]),
        'kinetic-energy cutoff units': line.split()[4]
    }

def _parse_total_energy(line, lines):
    total_energy = line.partition("=")[2].split()
    return {
        'total energy': float(total_energy[0]),
        'total energy units': total_energy[1]
    }

def _parse_bfgs(line, lines):
    toks = line.split()
    result = {'scf cycle count': int(toks[3]), 'bfgs step count': int(toks[7])}
    newline = next(lines).split()
    result['energy criteria'] = float(newline[3].rstrip(','))
    result['force criteria']  = float(newline[6].rstrip(','))
    result['cell criteria']   = float(newline[9].rstrip(')'))
    return result

def _parse_electronic_convergence(line, lines):
    return {'number of electronic iterations for convergence': int(line.split()[5])}

def _parse_pseudopotential(line, lines):
     newline = next(lines)
     return {'pseudopotential file': newline.split()[0]}

def _parse_ldau(line, lines):
    result = {'LDA+U l_max': line.split()[5].rstrip(")"), 'LDA+U parameters': {}}
    next(lines)
    newline = next(lines).split()
    while len(newline) > 1:
        result['LDA+U parameters'][newline[0]] = {
            'L': int(newline[1]),
            'U': float(newline[2]),
            'alpha': float(newline[3]),
            'J0': float(newline[4]),
            'beta': float(newline[5])
        }
    return result

def _parse_bravais_lattice(line, lines):
    return {"bravais-lattice index": int(line.partition("=")[2])}

def _parse_unit_cell_volume(line, lines):
    toks = line.partition("=")[2].split()
    return {
        "unit-cell volume": float(toks[0]),
        "unit-cell volume units": toks[1]
    }

def _gen_energy_contrib(name):
    def _extract(line, lines):
        line.partition("=")[2].split()
        return {
            "{} energy contribution".format(name): float(toks[0]),
            "{} energy contribution units".format(name): toks[1]
        }
    return (lambda x: "{} contribution".format(name) in x, _extract)

def _parse_stress(line, lines):
    pressure = float(line.rpartition("=")[2])
    stress = []
    for i in range(3):
        newline = next(lines)
        stress.append([float(x) for x in newline.split()[3:]])
    return {
        "pressure": pressure,
        "pressure units": "kbar",
        "stress": stress,
        "stress units": "kbar"
    }

base_rules = [
  (lambda x: "lattice parameter" in x, _parse_lattice_parameter),
  (lambda x: "Program PWSCF" in x, _parse_header),
  (lambda x: "Exchange-correlation" in x, _parse_xc),
  (lambda x: "kinetic-energy cutoff" in  x, _parse_cutoff),
  (lambda x: "total energy" in x and "=" in x, _parse_total_energy),
  (lambda x: "bfgs converged in" in x, _parse_bfgs),
  (lambda x: "convergence has been achieved in" in x, _parse_electronic_convergence),
  (lambda x: "PseudoPot. #" in  x, _parse_pseudopotential),
  (lambda x: "Simplified LDA+U calculation" in  x, _parse_ldau),
  (lambda x: "bravais-lattice index" in x, _parse_bravais_lattice),
  (lambda x: "unit-cell volume" in x, _parse_unit_cell_volume),
  (lambda x: "total   stress" in x, _parse_stress),
  _gen_energy_contrib("one-electron"),
  _gen_energy_contrib("hartree"),
  _gen_energy_contrib("xc"),
  _gen_energy_contrib("ewald")
]

class PwscfStdOutputParser(BlockParser):

    def __init__(self, rules=base_rules):
        super().__init__()
        for rule in rules:
            self.add_rule(rule)

