import numpy as np
import math
from matplotlib import pyplot
from matplotlib import pylab
import matplotlib.mlab as mlab
from scipy.special.orthogonal import eval_genlaguerre as laguer
from scipy.linalg import expm
from scipy.stats import poisson as poi
from scipy.misc import factorial

'''setting default values'''
dsideband=1.
ddelta=2.8*2.*np.pi*1000000.
dnu=2.8*2.*np.pi*1000000.
domega=2.*np.pi*50000.
dnmax=20.
damax=1000.
plotting=False

class parameter:
    def __init__(self,nbar,sideband=dsideband,delta = ddelta,nu = dnu,omega = domega,nmax=dnmax,amax=damax,state='therm',plotgroundstatepop=False):
        #input of sideband is also possible but overwrites delta
        m=1.660538921*40*10**(-27)#Ca-40
        #m=1.660538921*9*10**(-27)#Be-9
        self.kb=1.38065*10**(-23)
        self.hbar=1.054571726*10**(-34)
        self.nbar=nbar
        self.nu=nu
        self.omega=omega
        self.amax=amax
        self.nmax=nmax
        self.plotgroundstatepop=plotgroundstatepop
        self.state=state
#        if state=='coh':
        self.poi=poi(nbar)
        self.eta = 2.*np.cos(np.pi/4)*np.pi/729*10**9*np.sqrt(self.hbar/(2.*m*nu)) #Ca-40
        #self.eta = 2.*np.cos(np.pi/4)*np.pi/313*10**9*np.sqrt(self.hbar/(2.*m*nu)) #Be-9
        #self.eta = 0.202
        #self.hbar=1
        #self.kb=1
        if not np.float32(sideband)==np.float32(dsideband):
            if not np.float32(delta)==np.float32(ddelta):
                print 'sideband and delta cannot be specified at the same time.\noverwriting sideband value.'
                print delta,ddelta,sideband
                self.delta=delta
                self.sideband=np.floor(delta/nu)
            else:
                self.sideband=sideband
                self.delta=sideband*nu
        else:
            if not delta==ddelta:
                self.delta=delta
                self.sideband=np.floor(delta/nu)
            else:
                self.sideband=sideband
                self.delta=sideband*nu

class Sideband:
    def __init__(self,nbar,sideband=dsideband,delta = ddelta,nu = dnu,omega = domega,amax=damax,state='therm',noout=False,autoset=True,plotgroundstatepop=False):
        self.p = parameter(nbar=nbar,sideband=sideband,delta=delta,nu=nu,omega=omega,amax=amax,state=state,plotgroundstatepop=plotgroundstatepop)
        if self.p.sideband<0:
            self.nplus=-self.p.sideband
            self.p.sideband=-self.p.sideband
        else:
            self.nplus=0
        if self.p.state == 'therm':
            self.pr=self.pnb
        elif self.p.state == 'coh':#Rabi Flops and Sidebands are OK; dephasing, local signal and discord have not been checked!
            self.pr=self.pc
        else:
            print 'Error, initial state not recognized.'
            
        if state=='coh' and autoset:
            minn=np.max((0,np.floor(nbar)-6*np.ceil(np.sqrt(nbar))))
            maxx=np.max((10,np.ceil(nbar)+6*np.ceil(np.sqrt(nbar))))
            self.n=np.linspace(minn,maxx,maxx-minn+1)
            if not noout:
                print 'autoset to {0} relevant states'.format(maxx-minn+1)
            self.p.amax=maxx
        else:
            self.n=np.linspace(0,self.p.amax,self.p.amax+1)
        
        one=np.sum(self.pr(self.n))+np.sum(self.pr(np.linspace(-self.nplus,-1,self.nplus)))
        if 1-one>0.0001:
            print 'Warning: amax may not be high enough for chosen value of nbar\n missing probability = {0}'.format(1-one)            

        if 1-one<-10**(-14):
            print 'Warning: Normalization error: Negative probability of {0}'.format(1-one)            
        
    def omegaeff(self,n):#diverges for n -> infinity
        sideband=self.p.sideband
        eta=self.p.eta
        omega=self.p.omega
        x=1.
        for k in np.linspace(1,sideband,sideband):
            x=x*(n+k)
        result = eta**sideband*omega/2.*np.exp(-eta**2./2.)*laguer(n,sideband,eta**2.)/np.sqrt(x)
        return result

    def pnb(self,n):#thermal state
        nb=self.p.nbar
        result=(nb/(nb+1.))**(n+self.nplus)/(nb+1.)
        return result
    
    def pc(self,n):#coherent state
        return self.p.poi.pmf(n+self.nplus)
    
    def cnm(self,n,m):
        return np.sqrt(self.p.poi.pmf(n+self.nplus)*self.p.poi.pmf(m+self.nplus))

    def rabiflop(self,t):
        n=self.n
        omega=self.p.omega
        nbar=self.p.nbar
        result=np.sum(self.pr(np.outer(n,np.ones_like(t)))*np.sin(np.outer(self.omegaeff(n),t)*2.*np.pi/omega)**2,axis=0)
        if self.p.plotgroundstatepop:
            result=1-result
        return result

    def localsignal(self,t0,t):
        n=self.n
        omega=self.p.omega
        omegaeff=self.omegaeff
        result=(2.*np.abs(np.sum(np.outer(self.pr(n),np.ones_like(t))*
                         np.sin(np.outer(omegaeff(n),np.ones_like(t))*t0*2.*np.pi/omega)*
                         np.cos(np.outer(omegaeff(n),np.ones_like(t))*t0*2.*np.pi/omega)*
                         np.sin(np.outer(omegaeff(n),t-np.ones_like(t0)*t0)*2.*np.pi/omega)*
                         np.cos(np.outer(omegaeff(n),t-np.ones_like(t0)*t0)*2.*np.pi/omega),axis=0))**2)
        return result
    
    def discord(self,t):
        n=self.n
        omega=self.p.omega
        omegaeff=self.omegaeff
        if self.p.state=='therm':
            result=(2.*np.sum(np.outer(self.pr(n)**2,np.ones_like(t))*np.sin(np.outer(omegaeff(n),t)*2.*np.pi/omega)**2*
                          np.cos(np.outer(omegaeff(n),t)*2.*np.pi/omega)**2,axis=0))
        elif self.p.state=='coh':
            result=0
            for m in n:
                result+=2.*(np.sum((np.outer(np.abs(self.cnm(n,m)),
                        np.ones_like(t))*np.sin(np.outer(omegaeff(n),t)*2.*np.pi/omega)*np.cos(np.outer(omegaeff(m),t)*2.*np.pi/omega))**2,axis=0))        
        return result
                
    def alteredevolution(self,t0,t):
        nbar=self.p.nbar
        omegaeff=self.omegaeff
        omega=self.p.omega
        n=self.n
        result=(np.sum(np.outer(self.pr(n),np.ones_like(t))*(np.sin(np.outer(omegaeff(n),np.ones_like(t))*t0*2.*np.pi/omega)**2.*np.cos(np.outer(omegaeff(n),t-np.ones_like(t0)*t0)*2.*np.pi/omega)**2+
                                 np.sin(np.outer(omegaeff(n),t-np.ones_like(t0)*t0)*2.*np.pi/omega)**2.*np.cos(np.outer(omegaeff(n),np.ones_like(t))*t0*2.*np.pi/omega)**2.),axis=0))
        if self.p.plotgroundstatepop:
            result=1-result
        return result
    
    def anaplot(self,tmin,tmax,steps,t0=0,dephasing=True,discord=False,lsig=False):
        #print 'generating analytical data...',
        self.x=np.linspace(tmin,tmax,steps)
        if dephasing and t0==0:
            print '\n   Warning: t0=0, dephasing has no effect'
            
        self.flop=self.rabiflop(self.x)

        if dephasing or lsig:
            parta=self.x[:np.floor((steps-1.)*(t0-tmin)/(tmax-tmin))+1]
            partb=self.x[np.floor((steps-1.)*(t0-tmin)/(tmax-tmin))+1:]

        if dephasing:
            self.deph=np.array(list(self.rabiflop(parta))+list(self.alteredevolution(t0,partb)))
            
        if lsig:
            self.lsig=np.array(list(np.zeros_like(parta))+list(self.localsignal(t0,partb)))
        
        if discord:
            self.disc=self.discord(self.x)
        #print 'done'

class numSideband:
    def __init__(self,nbar,sideband=dsideband,delta = ddelta,nu = dnu,omega = domega,nmax=dnmax,plotgroundstatepop=False):
        self.p = parameter(nbar=nbar,sideband=sideband,delta=delta,nu=nu,omega=omega,nmax=nmax,plotgroundstatepop=plotgroundstatepop)
        if self.p.sideband<0:
            self.p.nplus=-self.p.sideband
            self.p.sideband=-self.p.sideband
        else:
            self.nplus=0
        self.n=np.linspace(0,nmax,nmax+1)
        nmax=self.p.nmax
        hbar=self.p.hbar
        delta=self.p.delta
        eta=self.p.eta
        nu=self.p.nu
        omega=self.p.omega
        self.a=np.diag(np.sqrt(np.arange(1,nmax+1)),1)
        self.ad=np.diag(np.sqrt(np.arange(1,nmax+1)),-1)
        self.ada=np.dot(self.ad,self.a)
        self.H=-hbar*delta*np.kron(np.eye(nmax+1),[[1.,0],[0,0]])+hbar*nu*np.kron(self.ada, np.eye(2))+hbar*omega/2.*(np.kron(expm(1.j*eta*(self.a + self.ad)), [[0,1.],[0,0]])+np.kron(expm(-1.j*eta*(self.a + self.ad)), [[0,0],[1.,0]]))
    
    def gibbsstate(self):
        nb=self.p.nbar
        hbar=self.p.hbar
        kb=self.p.kb
        nu=self.p.nu
        T=hbar*nu/(kb*np.log((nb + 1.)/nb))
        Z=np.trace(expm(-hbar*nu*self.ada/(kb*T)))
        result = np.kron(expm(-hbar*nu*self.ada/(kb*T)),[[0,0],[0,1]])/Z
        if result[2*(self.p.nmax+1)-1,2*(self.p.nmax+1)-1]>0.0001:
            print 'Warning: nmax may not be high enough for chosen value of nbar'
        return result
    
    def coherentstate(self):
        nb=self.p.nbar
        zero=np.zeros_like(self.n)
        zero[0]=1
        result = np.exp(-nb)*np.kron(self.purestate(np.dot(expm(-np.sqrt(nb)*self.ad),zero)),[[0,0],[0,1]])
        if result[2*(self.p.nmax+1)-1,2*(self.p.nmax+1)-1]>0.0001 or self.p.nmax<nb:
            print 'Warning: nmax may not be high enough for chosen value of nbar'
        return result
        
    def purestate(self,x):
        result = np.outer(x.conj().T,x)    
        return result
        
    def propagate(self,rho0,t,t0=0):
        hbar=self.p.hbar
        nmax=self.p.nmax
        omega=self.p.omega
        ut=expm(-1.j*self.H*(t-t0)*2.*np.pi/(omega*hbar))
        umt=ut.conj().T
        result=np.dot(np.dot(ut,rho0),umt)
        return result

    def reduced(self,rhot,element='e'):
        if element == 'e':
            x1=0
            x2=0
        elif element == 'g':
            x1=1
            x2=1
        elif element == 'c':
            x1=1
            x2=0
        else:
            raise NotImplementedError('Unrecognized argument: Element of the reduced density matrix\nmust be either e, g or c')
        nmax=np.int64(self.p.nmax)
        k=np.arange(0,nmax+1-x1-x2)
        x=np.sum(rhot[2*k+x1,2*k+x2])
        return x
            
    def localdephasing(self,rhot):
        rhoprime=rhot
        nmax=self.p.nmax
        for i in np.arange(0,2*(nmax+1)):
            for k in np.arange(0,2*(nmax+1)):
                if (k+i)%2:
                    rhoprime[k,i]=0
        return rhoprime
    
    def numplot(self,rho0,tmin,tmax,steps,t0=0,dephasing=True,discord=False,lsig=False,coh=False,noout=False,statusreport=False):
        if noout:
            statusreport=False
        if not noout:
            print 'generating numerical data...'
        self.x=np.linspace(tmin,tmax,steps)
        if dephasing and t0==0 and not noout:
            print '   Warning: t0=0, dephasing has no effect'
 
        self.flop=np.zeros_like(self.x)
        if coh:
            s=' and coherences plot'
            self.cohr=np.zeros_like(self.x)
            self.cohi=np.zeros_like(self.x)
        else:
            s=''
        if not noout:
            print '   generating list for rabiflop plot'+s
        i=0
        if self.p.plotgroundstatepop:
            plotpop='g'
        else:
            plotpop='e'                
        for k in self.x:
            rhot=self.propagate(rho0, k)
            self.flop[i]=np.real(self.reduced(rhot,plotpop))
            if coh:
                y=self.reduced(rhot,'c')
                self.cohr[i]=np.real(y)
                self.cohi[i]=np.imag(y)
            if statusreport:
                print 'step '+str(i+1)+' of '+str(steps)
            i=i+1

        if dephasing or lsig:
            rhot0=self.localdephasing(self.propagate(rho0,t0))
            self.deph=1*self.flop
            i=0
            if not noout:
                print '   generating list for dephasing plot'
            for k in self.x:
                if k>t0:
                    self.deph[i]=np.real(self.reduced(self.propagate(rhot0,k-t0),plotpop))
                    if statusreport:
                        print 'step '+str(i+1)+' of '+str(steps)
                i=i+1
                
        if discord:
            if not noout:
                print '   generating list for discord plot'
            self.disc=np.zeros_like(self.x)
            i=0
            for k in self.x:
                m=self.propagate(rho0, k)-self.localdephasing(self.propagate(rho0, k))
                self.disc[i]=np.real(np.trace(np.dot(m,m)))
                if statusreport:
                    print 'step '+str(i+1)+' of '+str(steps)
                i=i+1
        
        if lsig:
            self.lsig=np.abs(self.flop-self.deph)
            
        if not noout:
            print 'done'

class plots():
    def __init__(self,nbar,sideband=dsideband,delta = ddelta,nu = dnu,omega = domega,state='therm'):
        self.nbar=nbar
        self.sideband=sideband
        self.delta = delta
        self.nu = nu
        self.omega = omega 
        self.state = state
        
    def makeplot(self,tmin,tmax,steps,nsteps=-1,dephasing=True,lsig=True,coh=True,discord=False,adiscord=False,ndiscord=False,t0=0,num=True,nmax=50.,amax=10000.,statusreport=False,plotgroundstatepop=False):
        nbar=self.nbar
        sideband=self.sideband
        delta = self.delta
        nu = self.nu
        omega = self.omega
        state = self.state 
        if discord:
            adiscord=ndiscord=True
        
        ymin=0
        ymax=1
        ysmin=0
        ysmax=.5
        fig1=pyplot.figure()
        dyn=Sideband(nbar,sideband=sideband,delta = delta,nu = nu,omega = omega,amax=amax,state=state,plotgroundstatepop=plotgroundstatepop)
        dyn.anaplot(tmin,tmax,steps,t0=t0,lsig=lsig,discord=adiscord,dephasing=dephasing)
        
        if coh and not num:
            print 'Warning: Coherences can only be plotted if numerical plot is used'
            
        if ndiscord and not num and not discord:
            print 'Warning: Numerical discord can only be plotted if numerical plot is used'
        
        if lsig and not dephasing:
            print 'Warning: Local signal is plotted without dephasing plot'
        
        numplot=0
        coplot=0
        lsplot=0
        discplot=0
        if num:
            numplot=1
            if coh:
                coplot=1
        if lsig:
            lsplot=1
        if adiscord or (ndiscord and num):
            discplot=1
        
        pyplot.subplot(1+lsplot+discplot,1+numplot+coplot,1)
        pyplot.title('Analytical, RWA, '+state)
        pyplot.plot(dyn.x,dyn.flop)
        pyplot.ylim( (ymin, ymax) )
        pyplot.xlim( (tmin, tmax) )
        m=pylab.unravel_index(np.array(dyn.flop).argmax(), np.array(dyn.flop).shape)
        print 'Flop maximum at {:.2f}'.format(dyn.x[m])+' -> Expected optimal t0 at {:.2f}'.format(dyn.x[m]/2.)
        if plotgroundstatepop:
            st='ground '
        else:
            st='excited '
        pyplot.ylabel(st+'state population')    
        s='nbar = {:.2f}'.format(nbar)+', amax = {:.1f}'.format(dyn.p.amax)+', sideband = {:.0f}'.format(sideband)
        if num:
            if nsteps==-1:
                nsteps=steps
            ndyn=numSideband(nbar,sideband=sideband,delta = delta,nu = nu,omega = omega,nmax=nmax,plotgroundstatepop=plotgroundstatepop)
            if state=='therm':
                r=ndyn.gibbsstate()
            elif state=='coh':
                r=ndyn.coherentstate()
            else:
                print 'Error, initial state not recognized.'
            s=s+', purity = {:.4f}'.format(np.trace(np.dot(r,r)))+', nmax = {0}'.format(nmax)
        if dephasing:
            pyplot.plot(dyn.x,dyn.deph)
            pyplot.axvline(x=t0,ls=':',color='k')
            s=s+', t0 = {0}'.format(t0)
        pyplot.annotate(s, xy=(0.,-0.1-1.3*(lsplot+discplot)), xycoords='axes fraction')
        if lsig:
            pyplot.subplot(1+lsplot+discplot,1+numplot+coplot,2+numplot+coplot)
            pyplot.plot(dyn.x,dyn.lsig)
            pyplot.ylim( (ysmin, ysmax) )
            pyplot.xlim( (tmin, tmax) )        
            pyplot.axvline(x=t0,ls=':',color='k')
            pyplot.ylabel('local signal')
        
        if adiscord:
            pyplot.subplot(1+lsplot+discplot,1+numplot+coplot,2+coplot+lsplot*(1+numplot+coplot)+numplot)
            pyplot.plot(dyn.x,dyn.disc)
            pyplot.ylabel('discord')
            pyplot.xlim( (tmin, tmax) )
            pyplot.axvline(x=t0,ls=':',color='k')  
                   
        if num:
            ndyn.numplot(r,tmin,tmax,nsteps,t0=t0,lsig=lsig,discord=ndiscord,coh=coh,statusreport=statusreport,dephasing=dephasing)
            pyplot.subplot(1+lsplot+discplot,1+numplot+coplot,1+numplot)
            pyplot.title('Numerical, no RWA, '+state)
            pyplot.plot(ndyn.x,ndyn.flop)
            pyplot.ylim( (ymin, ymax) )
            pyplot.xlim( (tmin, tmax) )
            if dephasing:
                pyplot.axvline(x=t0,ls=':',color='k')
                pyplot.plot(ndyn.x,ndyn.deph)
            if lsig:
                pyplot.subplot(1+lsplot+discplot,1+numplot+coplot,3+numplot+coplot)
                pyplot.plot(ndyn.x,ndyn.lsig)
                pyplot.ylim( (ysmin, ysmax) ) 
                pyplot.axvline(x=t0,ls=':',color='k')
                pyplot.xlim( (tmin, tmax) )
            if ndiscord:
                pyplot.subplot(1+lsplot+discplot,1+numplot+coplot,4+coplot+lsplot*(1+numplot+coplot))
                pyplot.plot(ndyn.x,ndyn.disc)
                pyplot.axvline(x=t0,ls=':',color='k')
                pyplot.xlim( (tmin, tmax) )
            if coh:
                pyplot.subplot(1+lsplot+discplot,1+numplot+coplot,1+numplot+coplot)
                pyplot.title('Coherences')
                pyplot.plot(ndyn.x,ndyn.cohr,ndyn.x,ndyn.cohi)
                pyplot.axvline(x=t0,ls=':',color='k')
                pyplot.xlim( (tmin, tmax) )

    def contour(self,tmin,tmax,t0min=-1,t0max=-1,steps=100.,amax=3000.,showopt=True,statusreport=False):
        if t0min<0:
            t0min=tmin
        if t0max<0:
            t0max=tmax    
        nbar=self.nbar
        sideband=self.sideband
        delta = self.delta
        nu = self.nu
        omega = self.omega
        Z=list(np.zeros((steps,steps)))
        z=list(np.zeros(steps))
        xdelta = (tmax-tmin)/steps
        ydelta = (t0max-t0min)/steps
        x = np.arange(tmin, tmax, xdelta)
        y = np.arange(t0min, t0max, ydelta)
        X, Y = np.meshgrid(x, y)
        dyn=Sideband(nbar=nbar,sideband=sideband,delta = delta,nu = nu,omega = omega,amax=amax)
        print 'generating list for analytical contour plot'
        half=False
        index=0
        for i in y:
            try:
                Z[index]=dyn.localsignal(i,x+i)
                z[index]=np.sum(Z[index])/steps
            except IndexError:
                print 'Warning: index ran out of range, removing last element'
                t=list(X)
                t.pop()
                X=np.array(t)
                t=list(Y)
                t.pop()
                Y=np.array(t)
            if i>(t0max-t0min)/2.+t0min and not half:
                print '    50% done'
                half=True
            if statusreport:
                print 'step '+str(index+1)+' of '+str(len(y))
            index=index+1
        print 'done'
        fig2=pyplot.figure()
        pyplot.title('Analytical local signal')
        pyplot.xlabel('t+t0')
        pyplot.ylabel('t0')
        pyplot.contourf(X, Y, Z)
        if showopt:
            m=pylab.unravel_index(np.array(Z).argmax(), np.array(Z).shape)
            pyplot.annotate('nbar = {:.2f}'.format(nbar)+'. Optimal t0 in plotted range is {:.6f}'.format(X[m])+'. Highest contrast is {:.2f}'.format(np.array(Z).max()),xy=(0.,-0.115), xycoords='axes fraction')
            pyplot.axvline(x=X[m],ls=':',color='k')
            pyplot.axhline(y=Y[m],ls=':',color='k')
        
        fig3=pyplot.figure()
        pyplot.title('Time-averaged local signal')
        pyplot.xlabel('t0')
        pyplot.plot(Y,z)        
            
    def numcontour(self,tmin,tmax,t0min,t0max,steps,nmax=30.,showopt=True,statusreport=False):
        nbar=self.nbar
        sideband=self.sideband
        delta = self.delta
        nu = self.nu
        omega = self.omega 
        Z=list(np.zeros((steps,steps)))
        xdelta = (tmax-tmin)/steps
        ydelta = (t0max-t0min)/steps
        x = np.arange(tmin, tmax, xdelta)
        y = np.arange(t0min, t0max, ydelta)
        X, Y = np.meshgrid(x, y)
        dyn=numSideband(nbar=nbar, sideband=sideband, delta=delta, nu=nu, omega=omega, nmax=nmax)
        r=dyn.gibbsstate()
        print 'generating list for numerical contour plot'
        half=False
        index=0
        for i in y:
            dyn.numplot(r, tmin+i, tmax+i, steps, t0=i,lsig=True,noout=True)
            try:
                Z[index]=dyn.lsig
            except IndexError:
                print 'Warning: index ran out of range, removing last element'
                t=list(X)
                t.pop()
                X=np.array(t)
                t=list(Y)
                t.pop()
                Y=np.array(t)
            if i>(t0max-t0min)/2.+t0min and not half:
                print '    50% done'
                half=True
            if statusreport:
                print 'step '+str(index+1)+' of '+str(len(y))
            index=index+1
        print 'done'
        fig3=pyplot.figure()
        pyplot.title('Numerical local signal')
        pyplot.xlabel('t+t0')
        pyplot.ylabel('t0')
        pyplot.contourf(X, Y, Z)
        if showopt:
            m=pylab.unravel_index(np.array(Z).argmax(), np.array(Z).shape)
            pyplot.annotate('nbar = {:.2f}'.format(nbar)+'. Optimal t0 in plotted range is {:.6f}'.format(X[m])+'. Highest contrast is {:.2f}'.format(np.array(Z).max()),xy=(0.,-0.115), xycoords='axes fraction')
            pyplot.axvline(x=X[m],ls=':',color='k')
            pyplot.axhline(y=Y[m],ls=':',color='k')
            
    def frequencies(self,max_calc,nmax=0,detail=False):
        print 'plot for relevant frequencies is generated...',
        if nmax==0:
            nmax=max_calc
        nb=self.nbar
        state=self.state
        f2=pyplot.figure()
        x=Sideband(nb,amax=max_calc,noout=True,state=state,autoset=detail)
        pl1=f2.add_subplot(111)
        if x.p.state == 'therm':
            x.n=np.linspace(0, nmax, max_calc)
        omega=x.omegaeff(x.n)
        pl1.plot(x.n,omega)
        pl1.set_ylabel('Frequency $\Omega_n$')
        pl1.set_xlabel('n')
        pl2=pl1.twinx()
        
        prob=x.pr(x.n)
        pl2.plot(x.n,prob,'r')
        pl2.set_ylabel('Population')
        if state=='coh':
            pl2.axvline(nb-3*np.sqrt(nb),ls=':',color='k')
            pl2.axvline(nb,ls='--',color='k')
            pl2.axvline(nb+3*np.sqrt(nb),ls=':',color='k')
        print 'done'

#nb=15.
#pl=plots(nb,sideband=-1.,state='therm')# Be-9 omega=2*np.pi*500000.,nu=2*np.pi*11200000.
#pl.makeplot(tmin=0.,tmax=500.,steps=2500.,t0=1.49,amax=5000.,nmax=500.,num=False,statusreport=False,dephasing=True,lsig=False,discord=False,coh=True)
#pl.frequencies(nb,detail=False)
#pl.numcontour(0.,5.,0.,5.,50.,nmax=50.,statusreport=True)
#pl.contour(0.,10000.,t0min=0,t0max=100.,steps=500.,amax=40.,showopt=False)
#pyplot.show()