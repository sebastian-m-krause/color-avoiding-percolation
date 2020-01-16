from __future__ import division
from pylab import *
import scipy.optimize as opt
from scipy.stats import poisson
from scipy.misc import comb

"""
This file is used to generate theoretical predictions which are used to compare against the numerical results generated by the simulations.
"""



### Generating functions, here for Poisson, replace with scale-free, if needed
def gen_0(z,k):
    return exp(-k*(1.-z))

def gen_1(z,k):
    return exp(-k*(1.-z))


### For Calculating link failure probability u, in PRX Appendix eq. (B2)
def u(ks):
    u0=0.*ks
    for i in arange(len(ks)):
        u0[i]=opt.fixed_point(gen_1,0.5,args=[ks[i]])
    return u0


### For calculating link failure probability u_c
### without a color having frequency r_c.
### PRX Appendix Eq. (B4) (see special case given below there)
def func(z,ks,r_c):
    return r_c+(1.-r_c)*gen_1(z,ks)

def u_c(ks,r_c):
    u0=0.*ks
    for i in arange(len(ks)):
        u0[i]=opt.fixed_point(func,0.5,args=[ks[i],r_c])
    return u0

def S_ER():
    '''
    ER network percolation function returns the function, not the value
    :param k: average degree
    :return: percolation profile function
    '''

    def f(k):
        return opt.fsolve(lambda x: x - (1 - np.exp(-k * x)), 0.5, full_output=False)

    return f

def S_infER():

    '''

    :param k:
    :return:
    '''

    def f(k):
        u = opt.fsolve(lambda x : x - np.exp(-k*(1 - x)), 0.5, full_output=False)
        return 1 - np.exp(k*(u-1))*(k*(1-u) + 1 )

    return f

def get_theory(C=3,type="log10"):
    ### Specify parameters:
    ### nr of colors, homogeneous color frequency r_c
    #C=10
    r_c=1./C
    ### critical expected degree
    k_crit=1.*C/(C-1)
    ### array of values of expected degrees
    #ks=linspace(k_crit,.,1000)
    ks=logspace( -5, 0,1000) + k_crit if type == "log10" else linspace(0,6,1000)


    ### calculate arrays of link failure probabilities
    us=u(ks)                                                    ### PRX Appendix eq. (B2)
    u_cs=u_c(ks,r_c)                                            ### PRX Appendix eq. (B4)
    U_cs=1.+0.*ks                                               
    ### the following is not well done, as it includes a hard set numerical error
    index=u_cs<1.-1e-10
    U_cs[index]=1.-(1.-u_cs[index])/(1.-us[index])/(1.-r_c)     ### PRX Appendix eq. (B5)


    ### Just replace the calculation of the arrays 'us' etc. by better code, if you like
    ### Important is the following:
    ### Calculate S_color using closed form in PRX Appendix eq. (C11).
    ### Works up to about 20 colors, problems with 'C choose j' above
    S_color=1.+0.*ks
    for j in arange(1,C+1):
        S_color+=(-1.)**j*comb(C,j)*gen_0(us+(1.-us)*(j*r_c*U_cs**(j-1)+(1.-j*r_c)*U_cs**j),ks)


    ### plot and show
    #loglog(ks-k_crit,S_color,'.-', label="C=%i"%C)
    return [ks-k_crit,S_color] if type=="log10" else [ks,S_color]

