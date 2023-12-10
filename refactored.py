import argparse
import threading
from queue import Queue

def read_file(filename):
    try:
        with open(filename, 'r') as f:
            return [line.strip() for line in f]
    except FileNotFoundError:
        print(f"Could not open file: {filename}")
        return []

def generate_combinations(base_words, simple=False):
    suffixes = ['!', '@', '#', '$', '%', '^', '&', '*', '?'] + [str(i) for i in range(10)]
    for word in base_words:
        yield word
        if not simple:
            for suffix in suffixes:
                yield word + suffix

def process_passwords(passwords, user):
    for password in passwords:
        print(f'{user} {password}')

def worker(user_queue, password_generator):
    for password in password_generator:
        if user_queue.empty():
            return
        user = user_queue.get()
        process_passwords([password], user)
        user_queue.task_done()

def process_inputs(args):
    users = []
    companies = []
    words = []

    if args.users:
        if ',' in args.users:
            users = args.users.split(',')
        else:
            users = read_file(args.users)

    if args.companies:
        if ',' in args.companies:
            companies = args.companies.split(',')
        else:
            companies = read_file(args.companies)

    if args.words:
        if ',' in args.words:
            words = args.words.split(',')
        else:
            words = read_file(args.words)

    return users, companies, words

def main():
    parser = argparse.ArgumentParser(description='Weak Password Generator for PenTesting')
    parser.add_argument('-u', '--users', metavar="USERS", help='Comma delimited list of usernames or file with list of usernames.')
    parser.add_argument('-c', '--companies', metavar="COMPANIES", help='Comma delimited list of company names or file with list of company names.')
    parser.add_argument('-w', '--words', metavar="WORDS", help='Comma delimited list of words or file with list of words.')
    parser.add_argument('-x', '--exclude_defaults', action='store_true', help='Exclude default password list.')
    parser.add_argument('-s', '--simple', action='store_true', help='Generate simpler set of combinations.')
    parser.add_argument('-t', '--threads', type=int, default=4, help='Number of threads to use.')
    parser.add_argument('-i', '--input', action='store_true', help='Take additional words as input from the command line.')
    args = parser.parse_args()

    users, companies, words = process_inputs(args)

    if args.input:
        print("Enter additional words, one per line. Enter 'DONE' when finished:")
        while True:
            word = input()
            if word == 'DONE':
                break
            words.append(word)

    if not args.exclude_defaults:
        words.extend(["password", "passw0rd", ...])  # Extend with default passwords

    password_bases = companies + words + (users if users else [])
    password_generator = generate_combinations(password_bases, args.simple)

    user_queue = Queue()
    for user in users:
        user_queue.put(user)

    threads = []
    for _ in range(args.threads):
        thread = threading.Thread(target=worker, args=(user_queue, password_generator))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()


