'''
https://www.investopedia.com
sentdex python programming for finance
'''
def rotateTheString(originalString, direction, amount):
    Dict = {0: 0, 1: 0}
    ind = 0
    for x in direction:
        Dict[x] += amount[ind]
        ind += 1
    moves = Dict[0]-Dict[1]
    if(moves >= 0):    #rotate left
        Lfirst = originalString[moves:]
        Lsec = originalString[:moves]
        return (Lfirst+Lsec)
    else:
        Rfirst = originalString[moves:]
        Rsec = originalString[:moves]
        return(Rfirst+Rsec)



stri = "brainsd"
dir = [1,0]
amt = [7,6]
print(rotateTheString(stri, dir, amt))