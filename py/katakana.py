import sys

def add(dct: dict, english: tuple, katakana: tuple):
    assert len(english) == len(katakana)
    for eng, kat in zip(english, katakana):
        dct[eng] = kat

lookup = dict()

# single vowels
add(lookup, english=('a', 'i', 'u', 'e', 'o'), katakana=('ア', 'イ', 'ウ', 'エ', 'オ'))

# k + vowel
k = 'カ キ ク ケ コ キャ キュ キョ'
add(lookup, english=('ka', 'ki', 'ku', 'ke', 'ko', 'kya', 'kyu', 'kyo'), katakana=k.split())

# s + vowel
s = 'サ シ ス セ ソ シャ シュ ショ'
add(lookup, english='sa shi su se so sha shu sho'.split(), katakana=s.split())

# t + vowel
t = 'タ チ ツ テ ト チャ チュ チョ'
add(lookup, english='ta chi tsu te to cha chu cho'.split(), katakana=t.split())

# n + vowel
n = 'ナ ニ ヌ ネ ノ ニャ ニュ ニョ'
add(lookup, english='na ni nu ne no nya nyu nyo'.split(), katakana=n.split())

# h + vowel
h = 'ハ ヒ フ ヘ ホ ヒャ ヒュ ヒョ'
add(lookup, english='ha hi fu he ho hya hyu hyo'.split(), katakana=h.split())

# m + vowel
m = 'マ ミ ム メ モ ミャ ミュ ミョ'
add(lookup, english='ma mi mu me mo mya myu myo'.split(), katakana=m.split())

# y + vowel
add(lookup, english='ya yu yo'.split(), katakana='ヤ ユ ヨ'.split())

# r + vowel
r = 'ラ リ ル レ ロ リャ リュ リョ'
add(lookup, english='ra ri ru re ro rya ryu ryo'.split(), katakana=r.split())

# w + vowel
w = 'ワ ヰ ヱ ヲ'
add(lookup, english='wa wi we wo'.split(), katakana=w.split())

# n
add(lookup, english=('n',), katakana=('ン'))

# g + vowel
g = 'ガ ギ グ ゲ ゴ ギャ ギュ ギョ'
add(lookup, english='ga gi gu ge go gya gyu gyo'.split(), katakana=g.split())

# z + vowel
z = 'ザ ジ ズ ゼ ゾ ジャ ジュ ジョ'
add(lookup, english='za ji zu ze zo ja ju jo'.split(), katakana=z.split())

# d + vowel
d = 'ダ デ ド ヂャ ヂュ ヂョ'
add(lookup, english='da de do ja ju jo'.split(), katakana=d.split())

# b + vowel
b = 'バ ビ ブ ベ ボ ビャ ビュ ビョ'
add(lookup, english='ba bi bu be bo bya byu byo'.split(), katakana=b.split())

# p + vowel
p = 'パ ピ プ ペ ポ ピャ ピュ ピョ'
add(lookup, english='pa pi pu pe po pya pyu pyo'.split(), katakana=p.split())

# symbol
add(lookup, english='. -'.split(), katakana='・ ー'.split())

if __name__ == '__main__':
    for e in sys.argv[1:]:
        print(lookup[e], end='')
    print()
