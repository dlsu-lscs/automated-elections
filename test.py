fp = open('deletethis.csv', 'w')
for i in range(18):
    if i % 10 == 0:
        fp.close()
        fp = open('asdf' + str(i // 10) + '.csv', 'w')

    fp.write('hello' + str(i) + '\n')

fp.close()