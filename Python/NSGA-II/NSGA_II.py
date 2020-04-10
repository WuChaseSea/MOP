# -*-coding:UTF-8 -*-
'''
* NSGA_II.py
* @author wzm
* created 2020/04/09 22:40:50
* @function: 
'''
import math
import random
import matplotlib.pyplot as plt

# 约束函数1
def function1(x):
    value = -x**2
    return value
# 约束函数2
def function2(x):
    value = -(x-2)**2
    return value


'''
* @函数功能：查询列表中某一个值的下标值
* @说明：python列表中的index方法可以直接返回某个值的下标，并且是返回第一个值的下标，
但是如果没有查询到的话会报错，之后可以考虑try语句进行重构
'''
def index_of(a, list):
    for i in range(0, len(list)):
        if list[i] == a:
            return i
    return -1

'''
* @函数功能：依据values也就是某一维上的目标值对front上的点进行排序
* @参数说明：
front：当前种群的非支配解集
values：需要进行排序的某一维上的目标值
* @返回值：排序后的点的索引
'''
def sort_by_values(front, values):
    # 先定义一个空列表
    sorted_list = []
    # 循环，直到sorted_list和front的大小一样（因为只有front大小个点进行排序）
    while(len(sorted_list)!=len(front)):
        # 如果values中的最小值的索引是在front上的话
        if index_of(min(values), values) in front:
            sorted_list.append(index_of(min(values), values))
        # 不管最小值是否在front上，都应将其置为最大
        values[index_of(min(values), values)] = math.inf
    return sorted_list


'''
* @函数功能：快速非支配排序
* @参数说明：
values1：当前种群在第一个目标上的值
values2：当前种群在第二个目标上的值
* @返回值：当前种群的非支配解集，也可以说是分层之后的各个子集
'''
def fast_non_dominated_sort(values1, values2):
    # S表示点p支配的个体，是个二维数组
    S = [[] for i in range(0, len(values1))]
    front = [[]]
    # n表示点p被多少个个体所支配
    n = [0 for i in range(0, len(values1))]
    # rank表示该种群，表示该个体位于第几层
    rank = [0 for i in range(0, len(values1))]

    # 对种群中的每个点进行操作（注意这里p指的是该点的下标）
    for p in range(0, len(values1)):
        S[p] = []   # p点所支配的个体列表首先置空
        n[p] = 0    # p点被支配，也就是支配p点的个体数首先是0
        # 再遍历一遍种群中的所有点
        for q in range(0, len(values1)):
            # p支配q
            if (values1[p] > values1[q] and values2[p] > values2[q]) \
            or (values1[p] >= values1[q] and values2[p] > values2[q]) \
            or (values1[p] > values1[q] and values2[p] >= values2[q]):
                # p支配q并且q之前没有被添加到S列表中
                # （这里我觉得可以不用条件判断，本来就不会在S中）
                if q not in S[p]:
                    S[p].append(q)
            # q支配p
            elif (values1[q] > values1[p] and values2[q] > values2[p]) \
            or (values1[q] >= values1[p] and values2[q] > values2[p]) \
            or (values1[q] > values1[p] and values2[q] >= values2[p]):
                # 支配p点的个体数加一
                n[p] = n[p] + 1
        # 如果p点没有被任何点支配，就将p点的rank置0，并加入到当前种群的非支配解集中
        if n[p]==0:
            rank[p] = 0
            # 这里我觉得还是不需要用条件判断
            if p not in front[0]:
                front[0].append(p)
    # 通过两层for循环得到第一个子集之后，也就是P0，之后利用P0计算后面的子集
    i = 0
    # 判断当前层是否为空，不为空的话就计算下一子集
    while(front[i] != []):
        H = []
        # 对于当前子集中的所有个体
        for p in front[i]:
            # 对于当前子集中的某一个体，遍历被该点p支配的解集
            for q in S[p]:
                n[q] =n[q] - 1
                if( n[q] == 0): # 如果减了一之后等于0的话就说明该点之后没有被任何点支配
                    rank[q]=i+1 # 将该点放入第二层中
                    if q not in H:
                        H.append(q)
        i = i + 1
        front.append(H)
    del front[len(front)-1] # 最后while退出循环时最后一个子集为空，删除
    return front

'''
* @函数功能：拥挤距离的计算
* @参数说明：
values1：当前种群在第一个目标上的值
values2：当前种群在第二个目标上的值
front：当前种群中的非支配解集，这里的front指的是分层之后的某一层
* @说明：只对当前种群非支配解集中的个体进行拥挤距离的计算
* @返回值：当前非支配解集中的个体的拥挤距离
'''
def crowding_distance(values1, values2, front):
    # 初始化当前子集中每个个体的拥挤距离为0
    distance = [0 for i in range(0, len(front))]
    # 分别表示依据两个目标值对当前层的个体进行排序后的顺序
    sorted1 = sort_by_values(front, values1[:])
    sorted2 = sort_by_values(front, values2[:])
    # 将首尾的拥挤距离值置为无穷大
    distance[0] = math.inf
    distance[len(front) - 1] = math.inf
    # for k in range(1, len(front)-1):
    #     distance[k] = distance[k]+ (values1[sorted1[k+1]] - values2[sorted1[k-1]])/(max(values1)-min(values1))
    # for k in range(1,len(front)-1):
    #     distance[k] = distance[k]+ (values1[sorted2[k+1]] - values2[sorted2[k-1]])/(max(values2)-min(values2))
    # 计算个体的拥挤距离
    for k in range(1, len(front)-1):
        distance[k] = distance[k] + \
            (values1[sorted1[k+1]] - values1[sorted1[k-1]]) + \
                (values2[sorted1[k+1]] - values2[sorted1[k-1]])
    return distance

# 交叉
def crossover(a, b):
    r = random.random()
    if r>0.5:
        return mutation((a+b)/2)
    else:
        return mutation((a-b)/2)

# 变异
def mutation(solution):
    mutation_prob = random.random()
    if mutation_prob <1:
        solution = min_x + (max_x-min_x)*random.random()
    return solution

# 主程序运行
if __name__ == "__main__":
    pop_size = 50   # 种群大小
    max_gen = 100   # 最大进化代数
    # 初始化种群个体，生成50个范围在-10~10之间的个体
    min_x=-10
    max_x=10
    solution=[min_x+(max_x-min_x)*random.random() for i in range(0,pop_size)]
    gen_no=0    # 当前进化代数
    # 未达到最大进化代数之前一直进化，每一次进化表示一次繁殖
    while(gen_no<max_gen):
        # 计算当前种群个体在两个目标上的目标值，该值是一维的
        function1_values = [function1(solution[i]) for i in range(0,pop_size)]
        function2_values = [function2(solution[i]) for i in range(0,pop_size)]
        # 计算当前种群的非支配解集，该解集是二维的
        non_dominated_sorted_solution = fast_non_dominated_sort(function1_values[:],function2_values[:])
        # 显示当前种群的非支配解集
        print("第 ", gen_no, " 代最优的前沿是：")
        for valuez in non_dominated_sorted_solution[0]:
            print(round(solution[valuez],3), end=" ")
        print("\n")
        # 计算第一层个体的拥挤距离
        crowding_distance_values=[]
        for i in range(0,len(non_dominated_sorted_solution)):
            crowding_distance_values.append(crowding_distance(function1_values[:],function2_values[:],non_dominated_sorted_solution[i][:]))
        # solutionR表示下一代个体
        solutionR = solution[:]
        # 产生下一代个体
        while(len(solutionR)!=2*pop_size):
            a1 = random.randint(0,pop_size-1)
            b1 = random.randint(0,pop_size-1)
            solutionR.append(crossover(solution[a1],solution[b1]))
        function1_valuesR = [function1(solutionR[i]) for i in range(0,2*pop_size)]
        function2_valuesR = [function2(solutionR[i]) for i in range(0,2*pop_size)]
        # 计算下一代的非支配解集
        non_dominated_sorted_solutionR = fast_non_dominated_sort(function1_valuesR[:],function2_valuesR[:])
        # 计算下一代非支配解集中的拥挤距离
        crowding_distance_valuesR=[]
        for i in range(0,len(non_dominated_sorted_solutionR)):
            crowding_distance_valuesR.append(crowding_distance(function1_valuesR[:],function2_valuesR[:],non_dominated_sorted_solutionR[i][:]))
        # 从刚刚得到的2N个体中选出前N个
        new_solution = []
        # 依次遍历所有已分层的集合
        for i in range(0,len(non_dominated_sorted_solutionR)):
            # non_dominated_sorted_solutionR_1 = [index_of(non_dominated_sorted_solutionR[i][j], non_dominated_sorted_solutionR[i]) for j in range(0,len(non_dominated_sorted_solutionR[i]))]
            non_dominated_sorted_solutionR_1 = [j for j in range(0,len(non_dominated_sorted_solutionR[i]))]
            front2_t = sort_by_values(non_dominated_sorted_solutionR_1[:], crowding_distance_valuesR[i][:])
            front = [non_dominated_sorted_solutionR[i][front2_t[j]] for j in range(0,len(non_dominated_sorted_solutionR[i]))]
            front.reverse()
            for value in front:
                new_solution.append(value)
                if(len(new_solution)==pop_size):
                    break
            if (len(new_solution) == pop_size):
                break
        solution = [solutionR[i] for i in new_solution]
        gen_no = gen_no + 1

    function1 = [i * -1 for i in function1_values]
    function2 = [j * -1 for j in function2_values]
    plt.xlabel('Function 1', fontsize=15)
    plt.ylabel('Function 2', fontsize=15)
    plt.scatter(function1, function2)
    plt.show()
