#!/usr/bin/env python


import glob
import numpy as np

from amuse.ext.orbital_elements import orbital_elements
from amuse.io import write_set_to_file, read_set_from_file
from amuse.lab import Particles
from amuse.units import units, constants

from generate_resonant_chain import bring_planet_pair_in_resonance
from generate_resonant_chain import semi_to_orbital_period


def resonant_chain_planetary_system(bodies, tau_a_factor, t_evol, n_steps):
    """
    Iterate over adjacent planets and shake them into resonance.
    Args:
        bodies (Particles): The particles representing the planetary system.
        tau_a_factor (float): Migration parameter in terms of the outer orbital period.
        t_evol (float): Integration time in units of the outer orbital period.
        n_steps (int): Number of steps for the integration.
    Returns:
        Particles: The updated particles after creating the resonant chain.
    """
    for pi in range(len(bodies)-2):
        bodies = resonant_pair_planetary_system(
                        bodies=bodies,
                        inner_planet_id=pi,
                        tau_a_factor=tau_a_factor,
                        t_evol=t_evol,
                        n_steps=n_steps
                        )
    return bodies

def resonant_pair_planetary_system(bodies, inner_planet_id=0, outer_planet_id=1,
                                   tau_a_factor=-1e5, t_evol=100, n_steps=100):
    """
    Create a resonant pair of planets in a planetary system.
    Assumes host to be most massive particle in the system, planets to be all other
    massive particles.
    Args:
        bodies (Particles): The particles representing the planetary system.
        inner_planet_id (int): Index of the inner planet.
        outer_planet_id (int): Index of the outer planet.
        tau_a_factor (float): Migration parameter in terms of the outer orbital period.
        t_evol (float): Integration time in units of the outer orbital period.
        n_steps (int): Number of steps for the integration.
    """
    star = bodies[bodies.mass.argmax()]
    planets = bodies[bodies.type=="PLANET"]
    for pi in planets:
        orbital_elements = orbital_elements(star + pi)
        pi.sma = orbital_elements[2]

    planet_a = planets[inner_planet_id]
    planet_b = planets[outer_planet_id]
    Porb_a = semi_to_orbital_period(planet_a.sma, star.mass + planet_a.mass)[0]
    Porb_b = semi_to_orbital_period(planet_b.sma, star.mass + planet_b.mass)[0]
    if np.isnan(Porb_a.value_in(units.s)) or np.isnan(Porb_b.value_in(units.s)):
        print("Ill-defined orbital periods, returning original bodies")
        return bodies
    
    bring_planet_pair_in_resonance(
        planetary_system=bodies, 
        outer_planet=planet_b,
        tau_a_factor=tau_a_factor,
        t_evol=t_evol, 
        n_steps=n_steps
    )
    return bodies

def new_option_parser():
    from amuse.units.optparse import OptionParser
    result = OptionParser()
    result.add_option("--inner", dest="inner_planet_id",
                      type="int", default = 0,
                      help="inner planet id [%default]")
    result.add_option("--outer", dest="outer_planet_id",
                      type="int", default = 1,
                      help="outer planet id [%default]")
    result.add_option("-f", dest="infilename", 
                      default = "input_filename.amuse",
                      help="input infilename [%default]")
    result.add_option("-F", dest="outfilename", 
                      default = "output_filename.amuse",
                      help="output infilename [%default]")
    result.add_option("--n_steps", dest="n_steps", 
                      default = 100, type="int",
                      help="number of steps [%default]")
    result.add_option("--t_evol", dest="t_evol", 
                      default = 1000, type="float",
                      help="integration time in units of the outer orbital period [%default]")
    result.add_option("--tau", dest="tau_a_factor", 
                      type="float", default = -1e5,
                      help="migration parameter (in terms of outer orbital period) [%default]")
    return result
    
if __name__ in ('__main__', '__plot__'):
    o, arguments  = new_option_parser().parse_args()

    system = read_set_from_file("planetary_system.hdf5")
    if len(system) < 3:
        print(f"System has 1 planet, skipping")
        exit(-1)
    
    host = system[system.mass.argmax()]
    system = system.sorted_by_attribute("sma")
    p = system - host
    
    
    print(f"Original attributes:")
    print(f"Masses: {system.mass}")
    for pl in p:
        ke = orbital_elements(pl + host, G=constants.G)
        print(f"ecc={ke[3]}, ", end=" ") 
        print(f"sma={ke[2].in_(units.au)}", end=" ")
        print(f"inc={ke[5].in_(units.deg)}")

    system = resonant_chain_planetary_system(system, o.tau_a_factor, o.t_evol, o.n_steps)
    host = system[system.mass.argmax()]
    p = system - host
    print(f"After shaking:")
    print(f"Masses: {system.mass}")
    for pl in p:
        ke = orbital_elements(pl + host, G=constants.G)
        print(f"ecc={ke[3]}, ", end=" ") 
        print(f"sma={ke[2].in_(units.au)}", end=" ")
        print(f"inc={ke[5].in_(units.deg)}")
        
    if np.isnan(host.x.value_in(units.pc)):
        print("!!! Task unsuccessful: Resonance not found. !!!")
        exit(-1)
    
    write_set_to_file(system, o.outfilename, "hdf5", append_to_file=False)