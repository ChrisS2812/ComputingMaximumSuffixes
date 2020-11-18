import matplotlib.pyplot as plt
plt.rc('axes', axisbelow=True)
alg1 = [48, 1016, 37657+46479, 7039019, None]
alg2 = [41, 635, 21014+13307, 2068915, None]
alg3 = [39, 551, 17178+6589, 612638, -1]
alg4 = [39, 533, 16618+6589, 597611, -1]
alg5 = [33, 437, 11174+3051, 285115, -1]

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
