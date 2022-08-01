# coding:utf-8
from operator import contains
from platform import platform
import random
import argparse
import os
def pow_mod(p, q, n):
    '''
    幂模运算，快速计算(p^q) mod (n)
    这里采用了蒙哥马利算法
    '''
    res = 1
    while q :
        if q & 1:
            res = (res * p) % n
        q >>= 1
        p = (p * p) % n
    return res

def gcd(a,b):
    '''
    欧几里得算法求最大公约数
    '''
    while a!=0:
        a, b =b%a , a
    return b

def mod_1(x, n):
    '''
    扩展欧几里得算法求模逆
    取模负1的算法:计算x2= x^-1 (mod n)的值
    '''
    x0 = x
    y0 = n
    x1 = 0
    y1 = 1
    x2 = 1
    y2 = 0
    while n != 0:
            q = x // n
            (x, n) = (n, x % n)
            (x1, x2) = ((x2 - (q * x1)), x1)
            (y1, y2) = ((y2 - (q * y1)), y1)
    if x2 < 0:
            x2 += y0
    if y2 < 0:
            y2 += x0
    return x2

def probin(w):
    '''
    随机产生一个伪素数，产生 w表示希望产生位数
    '''
    list = []
    list.append('1')  #最高位定为1
    for i in range(w - 2):
        c = random.choice(['0', '1'])
        list.append(c)
    list.append('1') # 最低位定为1
    # print(list)
    res = int(''.join(list),2)
    return res


def prime_miller_rabin(a, n): # 检测n是否为素数
    '''
    第一步，模100以内的素数，初步排除很显然的合数
    '''
    Sushubiao=(2,3,5,7,11,13,17,19,23,29,31,37,41
                ,43,47,53,59,61,67,71,73,79,83,89,97)# 100以内的素数，初步排除很显然的合数
    for y in Sushubiao:
        if n%y==0:
            #print("第一步就排除了%d                 %d"%(n,y))
            return False
    #print('成功通过100以内的素数')

    '''
    第二步 用miller_rabin算法对n进行检测
    '''
    if pow_mod(a, n-1, n) == 1: # 如果a^(n-1)!= 1 mod n, 说明为合数
        d = n-1 # d=2^q*m, 求q和m
        q = 0
        while not(d & 1): # 末尾是0
            q = q+1
            d >>= 1
        m = d
        for i in range(q): # 0~q-1, 我们先找到的最小的a^u，再逐步扩大到a^((n-1)/2)
            u = m * (2**i)  # u = 2^i * m
            tmp = pow_mod(a, u, n)
            if tmp == 1 or tmp == n-1:
                # 满足条件 
                return True
        return False
    else:
        return False
def prime_test(n, k):
    while k > 0:
        a = random.randint(2, n-1)
        if not prime_miller_rabin(a, n):
            return False
        k = k - 1
    return True
# 产生一个大素数(bit位)
def get_prime(bit):
    while True:
        prime_number = probin(512)
        for i in range(50):  # 伪素数附近50个奇数都没有真素数的话，重新再产生一个伪素数
            u = prime_test(prime_number, 5)
            if u:
                break
            else:
                prime_number = prime_number + 2*(i)
        if u:
            return prime_number
        else:
            continue
# 将字符串型的数据转换成int型和将int型数据转换为字符串型
def str_int(str, mode):
    num = 0
    if(mode == 'toi'):
        # 将字符串型转换为int型
        # 判断一下当前传入的是否是16进制字符
        if("0x" in str):
            return int(str, 16)
        Mes = [] # 一个元组，用来保存一个字母对应的01序列
        for i in str:
            j = ord(i) # 将字符类型转换成
            
            m = []
            for k in range(8):# 看这一个整数的低8位的01情况
                if j & 1 == 1:
                    m.append('1')
                else:
                    m.append('0')
                j = j >> 1
            m.reverse()
            Mes += m
        num = int(''.join(Mes), 2)
        return num
    elif (mode == 'tos'):
        i = str.bit_length() + 1
        mes = []
        while i > 0:
            m = str & 0b11111111
            mes.append(chr(m))
            str = str >> 8
            i -= 8
        str = ""
        mes.reverse()   
        for i in mes:
            str += i
        return str


# 用于对文件整体进行加密或者解密的操作
def encode_file(name, e, n):
# 打开文件，读取文件内容并加密
    f = open(name, 'r')
    strs = []
    # 对文件内容逐行加密
    for line in f.readlines():
        line = line.rsplit('\n')[0]
        if(line != ''):
            if("0x" in line):# 如果当前读取的内容是已经加密的内容
                # 则直接对其进行叠加加密
                num = int(line, 16)
                num = pow_mod(num, e, n)
                strs.append(hex(num))
            else:
                num = str_int(line, mode='toi')
                num = pow_mod(num, e, n)
                strs.append(hex(num))    
    f.close

    f = open(name, 'w')
    for str in strs:
        f.write(str)
        f.write('\n')
    f.close
   
def decode_file(name, d, n):
    # 打开文件，读取文件内容并解密
    f = open(name, 'r')
    strs = []
    
    for line in f.readlines():
        line = line.rsplit('\n')[0]
        if(line != ''):
            num = int(line, 16)
            num = pow_mod(num, d, n)
            strs.append(hex(num)); 
    f.close
    f = open(name, 'w')
    for str in strs:
        f.write(str)
        f.write('\n')
    f.close
    f = open(name, 'r')
    strs = []
    for line in f.readlines():
        line = line.rsplit('\n')[0]
        if line != '':
            if("0x" in line):
                num = int(line, 16)
                strs.append(str_int(num, 'tos'))
            else :
                strs.append(line)
    f.close
    f = open(name, 'w')
    for str in strs:
        f.write(str)
        f.write('\n')
    f.close
    

def md5_encode(str, e, n):
    # 对传入的字符进行解密
    strs  = ""
    num = str_int(str, mode='toi')
    num = pow_mod(num, e, n)
    strs = hex(num)    
    if os.path.exists("a.txt"):
        os.remove("tmpfile/tmp")
    f = open('tmpfile/tmp','w')
    f.write(strs)
    f.close

def md5_decode(str, e, n):
    # 打开文件，读取文件内容并解密
    strs = ""
    num = int(str, 16)
    num = pow_mod(num, d, n)
    strs = str_int(num, "tos")
    if os.path.exists("a.txt"):
        os.remove("tmpfile/tmp")
    
    f = open('tmpfile/tmp','w')
    f.write(strs)
    f.close


# 打开密钥文件
def OP_key(name):
    f = open(name, 'r')
    line = f.readlines()
    num = int(line[0].rstrip('\n'), 16)
    big_ = int(line[1], 16)
    return num, big_
# 
# 将文件中的数字转换为字符串
#    


if __name__=='__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument('--c', nargs='+',help="创建RSA加密公钥和私钥并将其保存到文件中，需要指定文件目录", required=False)
    parse.add_argument('--ef',type=str ,nargs='+' ,help="对传入的文件进行加密",required=False)
    parse.add_argument('--df', type=str ,nargs='+', help='对传入的文件进行解密', required=False)
    parse.add_argument('--es',type=str ,nargs='+' ,help="对传入的字符串进行加密",required=False)
    parse.add_argument('--ds', type=str ,nargs='+', help='对传入的字符串进行解密', required=False)
    # parse.add_argument('--s', type=str ,nargs='+', help='将传入的文件中的内容从二进制转换为字符串', required=False)
    Cmd = parse.parse_args()

    if(Cmd.c != None):
        print("create key")
        p = get_prime(500) # 密钥p
        q = get_prime(550) # 密钥q
        n = p * q   # 公开n
        OrLa = (p-1)*(q-1)  # 欧拉函数
    
        while True: # 取一个合适的e，这里的e要和OrLa互素才行
            e = 65537
            if gcd(e, OrLa) == 1:
                break
            else:
                e = e-1
        d = mod_1(e, OrLa)
        f = open(Cmd.c[0]+'.pub','w')
        f.write(hex(e))
        f.write('\n')
        f.write(hex(n))
        f.close
        f = open(Cmd.c[0]+'.pri','w')
        f.write(hex(d))
        f.write('\n')
        f.write(hex(n))
        f.close
    # 用以对文件的加密
    # 加密的同时完成对文件中内容的转换
    if(Cmd.ef != None):
        e, n = OP_key(Cmd.ef[1])
        encode_file(Cmd.ef[0], e, n)

    if(Cmd.df != None):
        d, n = OP_key(Cmd.df[1])
        decode_file(Cmd.df[0], d, n)
# 对传入的字符串进行解密
    if(Cmd.es != None):
        e, n = OP_key(Cmd.es[1])
        md5_encode(Cmd.es[0], e, n)

    if(Cmd.ds != None):
        d, n = OP_key(Cmd.ds[1])
        md5_decode(Cmd.ds[0], d, n)
        
