#!/usr/bin/env python

# from amuse.community.rebound.interface import Rebound
from amuse.community.ph4.interface import ph4
from amuse.units import units, constants, nbody_system, quantities
from amuse.lab import Particles, Particle
from amuse.couple import bridge
from amuse.ext.orbital_elements import new_binary_from_orbital_elements, orbital_elements_from_binary

from tqdm import tqdm
import numpy as np
from amuse.io import write_set_to_file, read_set_from_file

import matplotlib.pyplot as plt
from fractions import Fraction

# # 1. Initialize a resonance

def semi_to_orbital_period(a, Mtot) :
    return 2*np.pi * (a**3/(constants.G*Mtot)).sqrt()

def orbital_period_to_semi(P, Mtot) :
    return ((constants.G*Mtot) * (P/(2*np.pi))**2)**(1./3.)

def test_resonance_period_ratio(bodies):

    import string

    star = bodies[bodies.type=="star"][0]    
    planets = bodies[bodies.type=="planet"]
    Porbit = [] | units.yr
    for i, pi in enumerate(planets):
        orbit = orbital_elements_from_binary(star + pi)
        pi.orbital_period = semi_to_orbital_period(orbit[2], star.mass+pi.mass)
        #pi.name = string.ascii_lowercase[i]
        print(f"Planet {pi.name} (a={orbit[2].value_in(units.au):.3f}au, e= {orbit[3]:.3f}): P= {pi.orbital_period.value_in(units.yr):.3f}year")

    for pi in planets:
        for pj in planets:
            if pi != pj:
                #print(pi, pj)
                fraction = Fraction(pi.orbital_period/pj.orbital_period).limit_denominator(10)
                print(f"{pi.name}, {pj.name} F={fraction}, "
                      f"Fraction= {fraction.numerator/fraction.denominator} "
                      f"Period ratio= {pi.orbital_period/pj.orbital_period}")

def test_resonance_by_integration(bodies, t_end, n_step):

    star = bodies[bodies.type=="star"][0]    
    planets = bodies[bodies.type=="planet"]
    orbit = orbital_elements_from_binary(star + planets[0])
    Porbit = semi_to_orbital_period(orbit[2], star.mass+planets[0].mass)
    
    converter = nbody_system.nbody_to_si(bodies.mass.sum(), Porbit)
    nbody = ph4(convert_nbody=converter)
    nbody.particles.add_particles(bodies)
    channel_from_system_to_framework = nbody.particles.new_channel_to(bodies)

    Porb = []
    sma = []
    ecc = []
    inc = []
    phi_a = []
    phi_b = []

    # nbody.get_time_step()
    time = [] | units.yr
    model_time = 0 | units.yr
    dt = t_end/n_step
    while nbody.model_time<=t_end:
        nbody.evolve_model(model_time)
        channel_from_system_to_framework.copy()
        model_time += dt
        time.append(model_time)

        name = []
        P = [] | units.yr
        a = [] | units.au
        e = []
        i = [] | units.deg
        p_a = [] 
        p_b = []
        phi = []
        inner_orbit = None
        outer_orbit = None
        for planet in planets:
            if outer_orbit is not None:
                inner_orbit = outer_orbit
            outer_orbit = orbital_elements_from_binary(star + planet)
            name.append(planet.name)
            P.append(semi_to_orbital_period(outer_orbit[2], star.mass))
            a.append(outer_orbit[2])
            e.append(outer_orbit[3])
            i.append(outer_orbit[5]|units.deg)

            if inner_orbit is not None:
                ta_a = inner_orbit[4]
                ta_b = outer_orbit[4]
                aop_a = inner_orbit[7]
                aop_b = outer_orbit[7]
                #phi = (ta_a+aop_a)-2*(ta_b+aop_b)
                phi = (ta_a)-2*ta_b 
                p_a.append(phi + aop_a)
                p_b.append(phi + aop_b)
            
        Porb.append(P.value_in(units.yr))
        sma.append(a.value_in(units.au))
        ecc.append(e)
        inc.append(i.value_in(units.deg))
        phi_a.append(p_a)
        phi_b.append(p_b)

    #print("phi_a:", phi_a)
    
    phi_a = np.array(phi_a).T
    phi_b = np.array(phi_b).T
    Porb = np.array(Porb).T
    #print(sma)
    sma = np.array(sma).T
    ecc = np.array(ecc).T
    inc = np.array(inc).T

    i = 0
    for ai in sma[:]:
        plt.plot(time.value_in(units.yr), ai, lw=3, label=name[i])
        i+= 1
    #plt.axhline(y=20.8, linestyle='-', lw=1)
    plt.xlabel('Time[yr]')
    plt.ylabel('a [au]')
    plt.legend()
    plt.show()

    for Pi in Porb[:]:
        plt.plot(time.value_in(units.yr), Pi, lw=3)
    #plt.axhline(y=20.8, linestyle='-', lw=1)
    plt.xlabel('Time[yr]')
    plt.ylabel('P [yr]')
    plt.show()
    
    for ei in ecc[:]:
        plt.plot(time.value_in(units.yr), ei)
    plt.xlabel('Time[yr]')
    plt.ylabel('e')
    plt.show()

    for ii in inc[:]:
        plt.plot(time.value_in(units.yr), ii)
    plt.xlabel('Time[yr]')
    plt.ylabel('i [deg]')
    plt.show()

    resonance = []
    for ni in range(len(name[:-1])):
        resonance.append(f"{name[ni]}-{name[ni+1]}")
    
    for pi in phi_a[:]:
        plt.scatter(time.value_in(units.yr), pi%(360))
    for pi in phi_b[:]:
        plt.scatter(time.value_in(units.yr), pi%(360))
    plt.xlabel('Time[yr]')
    plt.ylabel('phi [deg]')
    plt.show()

    for pi in range(len(phi_a[:])):
        plt.scatter(phi_a[pi]%(360), phi_b[pi]%(360), label=resonance[pi])
    plt.xlabel('phi a [deg]')
    plt.ylabel('phi b [deg]')
    plt.legend()

    plt.show()

def new_option_parser():
    from amuse.units.optparse import OptionParser
    result = OptionParser()
    result.add_option("-f", dest="infilename", 
                      default = "input_filename.amuse",
                      help="input infilename [%default]")
    result.add_option("-t", dest="t_end",
                      unit=units.yr,
                      type="float",
                      default = 1|units.yr,
                      help="end time [%default]")
    result.add_option("-n", dest="n_steps",
                      type="int",
                      default = 100,
                      help="number of steps [%default]")
    return result
    
if __name__ in ('__main__', '__plot__'):
    o, arguments  = new_option_parser().parse_args()

    bodies = read_set_from_file(o.infilename)
    test_resonance_period_ratio(bodies)
    test_resonance_by_integration(bodies, o.t_end, o.n_steps)

