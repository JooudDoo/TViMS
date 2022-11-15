import math as m
import re

spam_words = 0
ham_words = 0
spam_letters = 0
ham_letters = 0
dict_word = dict()  # word -> [0, 90]

# P(спам) = # спам–писем/# всех писем .
def p_spam(s_l, all_l):
    return s_l / all_l


# P({′купите′}|спам) = # спам–писем со словом ’купите’/# спам–писем
def p_word_in_spam(s_w_l, s_l):
    return (s_w_l + 1) / (s_l + 2)


# log(P(спам))+∑︁n k=1 log(P(wk|спам)) > log(P(не спам))+∑︁n k=1 log(P(wk|не спам)).
def p_bool(mail):
    all_letters = spam_letters + ham_letters
    words = set(re.findall(r'[a-zÀ-ÿ0-9_&\']+', mail))
    fst_p = m.log(p_spam(spam_letters, all_letters))
    snd_p = m.log(p_spam(ham_letters, all_letters))
    for word in words:
        list = dict_word.get(word)
        if list == None:
            list = [1, 1]
        fst_p += m.log(p_word_in_spam(list[0], (list[0]+list[1])))
        snd_p += m.log(p_word_in_spam(list[1], (list[0]+list[1])))
        #print(p_word_in_spam(list[0], spam_letters)+p_word_in_spam(list[1], ham_letters))
    return fst_p > snd_p

def brain ():
    global spam_letters,ham_letters, ham_words, spam_words
    with open("SMSSpamCollection.txt", "r", encoding='utf-8') as f:
        while True:
            file = f.readline().lower()
            if file == '':
                break

            if file[0] == 's':
                spam_letters += 1
            else:
                ham_letters += 1
            fil = set(re.findall(r'[a-zÀ-ÿ0-9_&\']+', file.split("\t", 1)[1]))
            for word in fil:
                if dict_word.get(word):  # ->[1,1]
                    list = dict_word.get(word)  # list[0] - spam, list[1] - not spam
                    if file[0] == 's':
                        spam_words += 1
                        list[0] += 1
                    else:
                        ham_words+= 1
                        list[1] += 1

                else:
                    list = [0, 0]
                    if file[0] == 's':
                        spam_words += 1
                        list[0] += 1
                    else:
                        ham_words += 1
                        list[1] += 1
                dict_word.update({word: list})

           #print(fil)



def accuracy():
    sucesessfull = 0
    faild = 0
    with open("primer.txt", "r", encoding='utf-8') as f:
        while True:
            file = f.readline().lower()
            if file == '':
                break
            ham_or_spam = file.split("\t", 1)[0]
            if ham_or_spam == "spam":
                ham_or_spam = True
            else:
                ham_or_spam = False
            result_class = p_bool(file.split("\t", 1)[1])
            if ham_or_spam == result_class:
                sucesessfull += 1
            else:
                faild += 1
    return sucesessfull/(sucesessfull + faild)

# print(spam_letters)
# print(ham_letters)
# print(dict_word)
brain()
print(accuracy())