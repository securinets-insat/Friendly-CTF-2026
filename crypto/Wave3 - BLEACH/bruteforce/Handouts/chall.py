#!/usr/bin/env -S python3 -u
flag = "000000000000000000000000000000000"
print("Don't even think to guess the flag , it is 33 characters long!")
user_input = input()
index = 0
for char in user_input:
    if char != flag[index]:
        print("Wrong flag!")
        exit()
    index += 1

print("Correct flag!")
print("flag is : Securinets{" +user_input + "}")