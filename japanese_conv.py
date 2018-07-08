# coding: utf-8
hiragana = "ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをん"
katakana = "ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴ"
hankana = ""
suuji = "0123456789０１２３４５６７８９"

def sort_str(string, reverse=False):
    return "".join(sorted(string, reverse=reverse))

def ishira(strj):
    return all([ch in hiragana for ch in strj])

def iskata(strj):
    return all([ch in katakana for ch in strj])

def iskatahira(strj):
    return all([ch in katakana or ch in hiragana for ch in strj])

def iskanji(strj):
    return all(["一" <= ch <= "龥" for ch in strj])    

def kata_to_hira(strj):
    return "".join([chr(ord(ch) - 96) if ("ァ" <= ch <= "ン") else ch for ch in strj])

def hira_to_kata(strj):
    return "".join([chr(ord(ch) + 96) if ("ぁ" <= ch <= "ん") else ch for ch in strj])

def hankaku_suuji(strj):
    dic2 = str.maketrans("０１２３４５６７８９", "0123456789")
    return strj.translate(dic2)