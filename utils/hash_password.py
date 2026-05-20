import sys
try:
    from werkzeug.security import generate_password_hash
except Exception:
    print("werkzeug is required. Install with: pip install werkzeug")
    sys.exit(1)


def main():
    if len(sys.argv) >= 2:
        pw = sys.argv[1]
    else:
        import getpass
        pw = getpass.getpass('Password: ')

    print(generate_password_hash(pw))


if __name__ == '__main__':
    main()
