 # -*- coding: utf-8 -*-


import math

class PropellerComputation:
    'output torque M Rpm N. Dp/Hp in m. Parameters in [A, epsilon, lambda, xi, e, Cfd, alpha0, K0]'
    DefaultParam = [5, 0.85, 0.75, 0.5, 0.83, 0.015, 0, 6.11]

    def __init__(self, T, Gp, rho, Dp = 0.72, Hp = 0.30, Bp = 2, param = DefaultParam):
        self.Dp = Dp
        self.Hp = Hp
        self.Bp = Bp
        self.Gp = Gp
        self.T = T
        self.rho = rho
        self.A = param[0]
        self.epsilon = param[1]
        self.lambda_coeff = param[2]
        self.xi = param[3]
        self.e = param[4]
        self.Cfd = param[5]
        self.a0 = param[6]
        self.K0 = param[7]
        self.C1 = 0
        self.Ct = 0
        self.Cd = 0
        self.Cm = 0
        self.N = 0
        self.M = 0
        self.__count_Cm()
        self.__count_M()
        self.P = self.M*self.N*2*math.pi/60

    def __count_Cd(self):
        theta0 = math.atan(self.Hp/(self.Dp*3.1415926))
        a_ab = self.epsilon*theta0 - self.a0
        self.C1 = self.K0*a_ab / (1 + self.K0/(3.1415926*self.A))
        self.Cd = self.Cfd + self.C1*self.C1/(3.1415926*self.A*self.e)

    def __count_Ct(self):
        self.__count_Cd()
        self.Ct = 0.25*(math.pi**2)*self.lambda_coeff*(self.xi**2)*self.Bp*self.C1/self.A

    def __count_Cm(self):
        self.__count_Ct()
        self.Cm = 0.25*math.pi**2*self.Cd*self.xi**2*self.lambda_coeff**2*self.Bp/self.A

    def __count_N(self):
        #print([self.T, self.rho, self.Dp, self.Ct])
        temp = self.T/(self.rho*self.Dp**4*self.Ct)
        self.N = 60*math.sqrt(temp)

    def __count_M(self):
        self.__count_N()
        self.M = self.rho*self.Dp**5*self.Cm*((self.N/60)**2)

    def __count_T(self):
        temp = (self.N/60)**2
        self.T = (self.rho*self.Dp**4*self.Ct)*temp


    def update(self, T , rho): #认为飞行中只有T、rho发生变化
        self.T = T
        self.rho = rho
        self.__count_Cm()
        self.__count_M()
        self.P = self.M * self.N * 2 * math.pi / 60

    def update_progressive(self, M, N, rho):
        self.M = M
        self.N = N
        self.rho = rho
        self.__count_T()
        self.P = self.M * self.N * 2 * math.pi / 60

    def get_P(self):
        return self.P

    def get_N(self):
        return self.N

    def get_M(self):
        return self.M

    def get_T(self):
        return self.T

