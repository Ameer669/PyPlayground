import numpy as np

lis = [[1,2,3,4],
    [5,6,7,8],
    [9,10,11,12],
    [13,14,15,16]]

#print(lis[2:][::-1])

mylist = np.array([
    [['a', 'b', 'c'], ['d','e','f'], ['g','h','i']],
    [['j','k','l'], ['m','n','o'], ['p','q','r']],
    [['s','t','u'], ['v','w','x'], ['y','z',' ']]
])


arr = np.array([[1,2,3,4],
                [5,6,7,8],
                [9,10,11,12],
                [13,14,15,16]])

#print(np.round(np.sqrt(arr[2: ,:1:-1] **np.pi)),end="\n\n")
#print(np.sqrt(arr[2: ,:1:-1] **np.pi))


print("\n\n")
word = 'This is Pakistan'
word = word[::-1]
words = word.split(" ")
words = words[::-1]
#print(word)

scores =np.array([[95, 85, 0, 65, 55, 100, 21, 46, -7],
                  [9, 70, 11, -1, 0, 99, 50, 39, 64]])
#print(scores[scores == 100] if scores[scores == 100] else None)
#print(np.where(scores == 100, 'Perfect',
               #np.where(scores < 50, 'Failed', 'Passed',)))
failed = scores[(scores < 50) & (scores > 0)] 
# | (or), & (and). cuz numpy uses C language
#print(failed)

mul1= np.array([[1,2,3,4,5,6,7,8,9,10]])
mul2= np.array([[1],[2],[3],[4],[5],[6],[7],[8],[9],[10]])
#print(mul1.shape)
#print(mul2.shape)
#print(mul1 * mul2)
#print(mul1 @ mul2)


rng = np.random.default_rng(seed=2)
#print(rng.integers(1, 100, size=(3, 4, 5)))
np.random.seed(2)
#print(np.random.uniform(1, 1.1, size=(3, 4, 3)))
a = np.array([1, 2, 3, 4, 5])
rng.shuffle(a)
#print(a)
