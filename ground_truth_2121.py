import json
# for temp-2121
#25.033009,121.555095
g = {}
g['0.2'] = 0
g['0.4'] = 0
g['0.6'] = 0
g['0.8'] = 1
g['1.0'] = 1
g['1.2'] = 1
g['1.4'] = 1
g['1.6'] = 1
g['1.8'] = 1
g['2.0'] = 1
g['2.2'] = 1
g['2.4'] = 1
g['2.6'] = 0
g['2.8'] = 0
g['3.0'] = 0
g['3.2'] = 0
g['3.4'] = 0
g['3.6'] = 0
g['3.8'] = 0
g['4.0'] = 0
g['4.2'] = 1
g['4.4'] = 0
g['4.6'] = 0


gj = json.dumps(g)
f = open("GT-2121.json","w")
f.write(gj)
f.close()