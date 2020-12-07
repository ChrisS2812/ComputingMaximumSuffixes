import matplotlib.pyplot as plt
plt.rc('axes', axisbelow=True)
alg3 = [48, 1016, 37657 + 46479, 7039019, None]
alg4 = [41, 635, 21014 + 13307, 2068915, None]
alg5 = [39, 551, 17178 + 6589, 612638, 128103369]
alg6 = [39, 533, 16618 + 6589, 597611, 118777832]
alg7 = [33, 437, 11174 + 3051, 285115, 50996293]
alg8 = [9, 108, 2178+1894, 64272, 8466331]

x = [0,1,2,3,4]

plt.scatter(x, alg3, marker='+', label="Algorithm 3")
plt.scatter(x, alg4, marker='x', label="Algorithm 4")
plt.scatter(x, alg5, marker=4, label="Algorithm 5")
plt.scatter(x, alg6, marker=5, label="Algorithm 6")
plt.scatter(x, alg7, marker=6, label="Algorithm 7")
plt.scatter(x, alg8, marker='*', c='#E5C900', label="Algorithm 8")
plt.xticks([0,1,2,3,4], ["$3$", "$4$", "$5$", "$6$", "$7$"])
plt.legend()
plt.grid()
plt.yscale('log')
plt.xlabel('$n$')
plt.ylabel("# calls to $checkFeasible$ upon calling $FindT(n)$")
plt.savefig("plots/nr_calls_optims.svg")
