import math

number = int(input())

for i in range(2, int(math.sqrt(number)) + 1): # обычно делитель не будет больше корня
    while number % i == 0: # while, а не if
        print(i)
        number //= i # убираем множитель из числа

if number != 1: # но один делитель может быть больше корня
    print(number)
