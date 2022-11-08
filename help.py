l = [1, 2, 3, 8]
i = [4, 5, 6, 7]
if any(r in l for r in i):
    print("yes")
else:
    print("no")