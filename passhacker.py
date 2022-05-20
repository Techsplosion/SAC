import os
from colorama import Fore

possible_password_containers = ['passwd', 'pass', 'passwords', 'password', 'credentials', 'cred', 'creds', 'credential']

to_check = []

for path, dirs, files in os.walk('C:\\'):
    print(Fore.YELLOW + f'[*] Checking {path}')
    for directory in dirs:
        for i in possible_password_containers:
            if i in directory:
                to_check.append(path + directory)
                print(Fore.GREEN + f'[+] Found {path}{directory}')
        else:
            print(Fore.RED + f'[-] {path}{directory} is not a password container')

print(Fore.RESET, end='')

for folder in to_check:
    for path, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith('.txt'):
                os.chdir(path)
                with open(file, 'r', encoding='utf-8') as f:
                    pf = f.read()
                pf = pf.split('\n')
                print(Fore.LIGHTGREEN_EX + f"Retrieved passwords from {path}\\{file}:")
                for line_num, line in enumerate(pf):
                    print(f'{line_num + 1}. {line}')

print(Fore.RESET, end='')
