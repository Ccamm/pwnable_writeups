# Pwnable.kr: Toddler's Bottle
## coin1

The challenge is quite simple, it is just beating a game finding a counterfeit coin among hundreds of normal coins. Not exactly possible by us humans, but we should be able to write a script to play the game for us. Opening up the game at *nc pwnable.kr 9007* we are greeted with the following screen.

<pre>
---------------------------------------------------
-              Shall we play a game?              -
---------------------------------------------------

You have given some gold coins in your hand
however, there is one counterfeit coin among them
counterfeit coin looks exactly same as real coin
however, its weight is different from real one
real coin weighs 10, counterfeit coin weighes 9
help me to find the counterfeit coin with a scale
if you find 100 counterfeit coins, you will get reward :)
FYI, you have 60 seconds.

- How to play -
1. you get a number of coins (N) and number of chances (C)
2. then you specify a set of index numbers of coins to be weighed
3. you get the weight information
4. 2~3 repeats C time, then you give the answer

- Example -
[Server] N=4 C=2 	# find counterfeit among 4 coins with 2 trial
[Client] 0 1 		# weigh first and second coin
[Server] 20			# scale result : 20
[Client] 3			# weigh fourth coin
[Server] 10			# scale result : 10
[Client] 2 			# counterfeit coin is third!
[Server] Correct!

- Ready? starting in 3 sec... -
</pre>

The first point for solving this challenge is that there is only one counterfeit coin and it must exist in either first half of coins or the second half. So we can find which half the counterfeit coin exists in by sending the indexes of the first half of the coins and if the server responds with an odd number then the counterfeit coin is in the half that we sent to the server. Otherwise it would be in the half that we did not send to the server.

We can recursively perform this search and narrow done our selection based on which half we find the counterfeit coin is in until we are left with just one coin. This is actually called a Binary Search.

Now we can write our neat little script in order to pwn this challenge.

```python
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

    # If we are left with any extra chances we should skip these
    for i in range(0, chances):
        c.sendline("0")
        c.recvline()

    c.sendline(result)
    c.recvline()

c.interactive()
```

We can now run this script to beat the game! I had to copy mine over to the pwnable server since my network response time was too slow to complete within 1 minute.

<pre>
[+] Opening connection to 0 on port 9007: Done


    ---------------------------------------------------

    -              Shall we play a game?              -

    ---------------------------------------------------



    You have given some gold coins in your hand

    however, there is one counterfeit coin among them

    counterfeit coin looks exactly same as real coin

    however, its weight is different from real one

    real coin weighs 10, counterfeit coin weighes 9

    help me to find the counterfeit coin with a scale

    if you find 100 counterfeit coins, you will get reward :)

    FYI, you have 60 seconds.



    - How to play -

    1. you get a number of coins (N) and number of chances (C)

    2. then you specify a set of index numbers of coins to be weighed

    3. you get the weight information

    4. 2~3 repeats C time, then you give the answer



    - Example -

    [Server] N=4 C=2     # find counterfeit among 4 coins with 2 trial

    [Client] 0 1         # weigh first and second coin

    [Server] 20            # scale result : 20

    [Client] 3            # weigh fourth coin

    [Server] 10            # scale result : 10

    [Client] 2             # counterfeit coin is third!

    [Server] Correct!



    - Ready? starting in 3 sec... -



Game Number: 0
Game Number: 1
Game Number: 2
Game Number: 3
Game Number: 4
Game Number: 5
Game Number: 6
Game Number: 7
Game Number: 8
Game Number: 9
Game Number: 10
Game Number: 11
Game Number: 12
Game Number: 13
Game Number: 14
Game Number: 15
Game Number: 16
Game Number: 17
Game Number: 18
Game Number: 19
Game Number: 20
Game Number: 21
Game Number: 22
Game Number: 23
Game Number: 24
Game Number: 25
Game Number: 26
Game Number: 27
Game Number: 28
Game Number: 29
Game Number: 30
Game Number: 31
Game Number: 32
Game Number: 33
Game Number: 34
Game Number: 35
Game Number: 36
Game Number: 37
Game Number: 38
Game Number: 39
Game Number: 40
Game Number: 41
Game Number: 42
Game Number: 43
Game Number: 44
Game Number: 45
Game Number: 46
Game Number: 47
Game Number: 48
Game Number: 49
Game Number: 50
Game Number: 51
Game Number: 52
Game Number: 53
Game Number: 54
Game Number: 55
Game Number: 56
Game Number: 57
Game Number: 58
Game Number: 59
Game Number: 60
Game Number: 61
Game Number: 62
Game Number: 63
Game Number: 64
Game Number: 65
Game Number: 66
Game Number: 67
Game Number: 68
Game Number: 69
Game Number: 70
Game Number: 71
Game Number: 72
Game Number: 73
Game Number: 74
Game Number: 75
Game Number: 76
Game Number: 77
Game Number: 78
Game Number: 79
Game Number: 80
Game Number: 81
Game Number: 82
Game Number: 83
Game Number: 84
Game Number: 85
Game Number: 86
Game Number: 87
Game Number: 88
Game Number: 89
Game Number: 90
Game Number: 91
Game Number: 92
Game Number: 93
Game Number: 94
Game Number: 95
Game Number: 96
Game Number: 97
Game Number: 98
Game Number: 99
[*] Switching to interactive mode
Congrats! get your flag
b1NaRy_S34rch1nG_1s_3asy_p3asy
</pre>
