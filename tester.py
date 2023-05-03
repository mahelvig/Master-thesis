a = 32 + 16 + 8 + 4

b = 16 + 4 + 1 

c = a & b

flag = 17

test = flag & (( 1|64 ) | 2  ) == 0 

d = flag // 16

print(d)

print(test)

df = 2
for i in range(10):
    print(f'\r{i}', end = '\r'+' '*26 )