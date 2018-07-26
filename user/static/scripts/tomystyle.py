# -*- coding: utf-8 -*-
import os
import sys
input_file_path = sys.argv[1]
file = open(input_file_path,'r')
res = ''
s = file.read()
lines = s.split("\n")
for l in lines:
    if l == '':
        break
    k = l.split('\t')
    digits = k[0]
    category =k[1]
    if category == 'figure':
        category = 'image'
    d = digits.split(',')
    # 左右上下 ==> 左上右下
    m = d[0] +' ' +d[2] +' ' +d[1] +' ' +d[3] +' ' + category +' ' + 'returned' + '\n'
    if category == 'image' or category == 'table' or category == 'formula':
        res += m
print res
file.close()
f = open(input_file_path,'wb')
f.write(res)
f.close()
