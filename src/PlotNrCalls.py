import matplotlib.pyplot as plt
plt.rc('axes', axisbelow=True)
alg1 = [48, 1016, 37657+46479, 7039019, None]
alg2 = [41, 635, 21146+15017, 2107054, None]
alg3 = [39, 551, 16317+8523, 583507, 101086131]
alg4 = [39, 551, 15719+6393, 541007, 93202436]
alg5 = [33, 456, 12328+4139, 408481, 94187922]

x = [0,1,2,3,4]

plt.scatter(x, alg1, marker='+', label="Algorithm 3 (non-optimized)")
plt.scatter(x, alg2, marker='x', label="Algorithm 4")
plt.scatter(x, alg3, marker=4, label="Algorithm 5 (best performing)")
plt.scatter(x, alg4, marker=5, label="Algorithm 6")
plt.scatter(x, alg5, marker=6, label="Algorithm 7 (fully optimized)")
plt.xticks([0,1,2,3,4], ["$3$", "$4$", "$5$", "$6$", "$7$"])
plt.legend()
plt.grid()
plt.yscale('log')
plt.xlabel('$n$')
plt.ylabel("# calls to $checkFeasible$ upon calling $FindT(n)$")
plt.savefig("test.svg")
plt.show()
