from pwn import *
import re

# Uncomment the line below if pwn script is loaded onto the pwnable server
# for faster response times. 
# c = remote("0", 9007)
c = remote("pwnable.kr", 9007)

#Parse the starting parameters of round
def parse_start(recved):
    recv_splt = recved.split(' ')
    result = [int(re.sub("\D", "", x)) for x in recv_splt]
    return result[0], result[1]

#Perform a binary search to find the counterfeit coin
def binary_search(mn, mid, mx, chances):
    if mx - mn == 1: return str(mn), chances
    query = ""
    for i in range(mn, mid):
        query += str(i) + " "

    c.sendline(query)
    chances -= 1

    if int(c.recvline()[:-1]) % 2 == 0:
        return binary_search(mid, int((mx-mid)/2)+mid, mx, chances)
    else: return binary_search(mn, int((mid-mn)/2)+mn, mid, chances)

#Skip the explanation
for i in range(0, 31):
    print(c.recvline())

#Perform 100 games
for game_num in range(0, 100):
    print("Game Number: " + str(game_num))
    n,chances = parse_start(c.recvline())
    result, chances = binary_search(0, int((n-1)/2), n-1, chances)

    for i in range(0, chances):
        c.sendline("0")
        c.recvline()

    c.sendline(result)
    c.recvline()

c.interactive()
