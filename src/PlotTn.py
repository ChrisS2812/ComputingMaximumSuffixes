import matplotlib.pyplot as plt

nrange = range(0,21)
yrange = range(0,30,2)
Tn_lower = [n-1 for n in nrange]
Tn_lower[0] = 0
Tn_upper = [int((4 * n / 3) - 5 / 3) for n in nrange]
Tn_upper[0] = 0
Tn_upper[1] = 0
Tn_upper[2] = 1

Tn_lower_new = [0,0,1,2,3,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
Tn_upper_new = list(Tn_upper)
Tn_upper_new[8] = 8


plt.plot(Tn_upper_new, label='New upper limit for $T(n)$', color='green')
plt.plot(Tn_upper, label='Previous upper limit for $T(n)$ [ ⌊$4/3n - 5/3$⌋ ]',
         color='red', linestyle=(0,(5,3)))
plt.plot(Tn_lower_new, label='New lower limit for $T(n)$', linestyle=(0,(5,5)))
plt.plot(Tn_lower, label='Previous lower limit for $T(n)$ [$n-1$]', linestyle=(0,(5,10)))

plt.fill_between(nrange, Tn_lower, Tn_upper, alpha=0.2, color='red',
                 hatch='/', label='Area of gained certainty')
plt.fill_between(nrange, Tn_lower_new, Tn_upper_new, alpha=0.3,
                 color='green', hatch='\\', label='Area of remaining uncertainty')
plt.xlabel('n')
plt.ylabel('max. nr. of three-way-comps. needed for solving $maxSuffix_n$')
plt.xticks(nrange)
plt.yticks(yrange)
plt.legend()
plt.grid()
plt.show()