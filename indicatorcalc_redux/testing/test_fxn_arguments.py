def test(val_one, val_two=val_one):
    print('val_one: ', val_one)
    print('val_two: ', val_two)


if __name__ == '__main__':
    test(val_one=1)

    test(val_one=1, val_two=2)
