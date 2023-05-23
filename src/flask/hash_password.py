import sys

from werkzeug.security import generate_password_hash


if __name__ == '__main__':
    try:
        plain_password = sys.argv[1]
        print(generate_password_hash(plain_password))
    except IndexError:
        ...
