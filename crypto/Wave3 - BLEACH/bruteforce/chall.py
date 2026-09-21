#!/usr/bin/env -S python3 -u
flag = "g3t_s𝔲g4_t3nsh0_f1n4l_Brut3_F0rc3"
print("Don't even think to guess the flag , it is 33 characters long!")
user_input = input()
print(len(flag))
index = 0
for char in user_input:
    if char != flag[index]:
        print("Wrong flag!")
        exit()
    index += 1

print("Correct flag!")
print("flag is : Securinets{" +user_input + "}")