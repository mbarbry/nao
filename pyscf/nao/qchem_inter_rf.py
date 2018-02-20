from __future__ import print_function, division
import sys, numpy as np
from numpy import diagflat, zeros, einsum
from pyscf.nao import scf
from copy import copy

class qchem_inter_rf(scf):
  """ Quantum-chemical interacting response function """
  
  def __init__(self, **kw):
    """ Constructor... """
    scf.__init__(self, **kw)

    nf = self.nfermi[0]
    nv = self.norbs-self.vstart[0]
    self.FmE = np.add.outer(self.ksn2e[0,0,self.vstart[0]:],-self.ksn2e[0,0,:self.nfermi[0]])
    self.sqrt_FmE = np.sqrt(self.FmE).reshape([nv*nf])
    self.kernel_qchem_inter_rf()
  
  def inter_rf(self, ww):
    """ This delivers the interacting response function in the product basis"""
    rf = np.zeros((len(ww), self.nprod, self.nprod), dtype=self.dtypeComplex)
    p,m,n = self.pmn2v.shape
    sp2v = np.dot(self.s2xpy, self.pmn2v.reshape(p,m*n).T)
    for iw,w in enumerate(ww):
      for iOmega,(Omega,p2v) in enumerate(zip(self.s2omega, sp2v)):
        p2z = p2v*(2.0/(w-Omega)-2.0/(w+Omega))
        rf[iw] += np.outer(p2z,p2v)
    return rf

  
  def kernel_qchem_inter_rf(self, **kw):
    """ This is constructing A B matrices and diagonalizes the problem """
    nf = self.nfermi[0]
    nv = self.norbs-self.vstart[0]
    vs = self.vstart[0]
    
    x = self.mo_coeff[0,0,:,:,0]
    pab2v = self.pb.get_ac_vertex_array()
    self.pmn2v = pmn2v = einsum('nb,pmb->pmn', x[:nf,:], einsum('ma,pab->pmb', x[vs:,:], pab2v))
    pmn2c = einsum('qp,pmn->qmn', self.hkernel_den, pmn2v)
    meri = -einsum('pmn,pik->mnik', pmn2c, pmn2v)
    #meri.fill(0.0)

    A = (diagflat( self.FmE ).reshape([nv,nf,nv,nf]) + meri).reshape([nv*nf,nv*nf])
    B = meri.reshape([nv*nf,nv*nf])
    assert np.allclose(A, A.transpose())
    assert np.allclose(B, B.transpose())

    ham_rpa = np.multiply(self.sqrt_FmE[:,None], np.multiply(A+B, self.sqrt_FmE))
    esq, self.s2z = np.linalg.eigh(ham_rpa)
    self.s2omega = np.sqrt(esq)
    self.s2z = self.s2z.T
    self.s2xpy = np.zeros_like(self.s2z)
    for s,(e2,z) in enumerate(zip(esq, self.s2z)):
      w = np.sqrt(e2)
      self.s2xpy[s] = np.multiply(self.sqrt_FmE, self.s2z[s])/np.sqrt(w)
      #print(e2, abs(np.dot(ham_rpa,z)-e2*z).sum())
    return self.s2omega,self.s2z
