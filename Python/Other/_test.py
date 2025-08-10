from SimpleTest import print_square

def test_print(capsys):
    print_square(3)
    captured = capsys.readouterr()
    assert captured.out == "###\n###\n###\n"
