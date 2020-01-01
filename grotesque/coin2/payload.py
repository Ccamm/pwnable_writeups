from pwn import *
import re

context.log_level = 'debug'

c = remote("pwnable.kr", 9008)

#Parse the starting parameters of round
def parse_start(recved):
    recv_splt = recved.split(' ')
    result = [int(re.sub("\D", "", x)) for x in recv_splt]
    return result[0], result[1]

"""
Finds the counterfeit coin by selecting the numbers with the ith bit set to 0b1 up to chances-1
When program returns, the selections with the counterfeit weights are which bit positions
need to be set to 1 in result.
"""
def find_counterfeit(n, chances):
    query_list = []
    for i in range(0,chances):
        query = ""
        bitmap = 0
        for j in range(0, n):      
            j |= 1 << i
            if (bitmap >> j) == 0b0 and j < n:
                query += str(j) + " "
                bitmap |= 1 << j
        query_list.append(query[:-1])

    c.sendline('-'.join(query_list))
    output_list = c.recvline()[:-1].split('-')
    
    result = 0
    for i in range(0, len(output_list)):
        if int(output_list[i]) % 2 == 1:
            result |= 1 << i
    return str(result)

#Skip the explanation
for i in range(0, 32):
    print(c.recvline())

#Perform 100 games
for game_num in range(0, 100):
    print("Game Number: " + str(game_num))
    n,chances = parse_start(c.recvline())
    c.sendline(find_counterfeit(n, chances))
    c.recvline()

c.interactive()
