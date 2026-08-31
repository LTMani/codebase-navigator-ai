import sys, base64
b64 = sys.argv[1].strip()
b64 += '=' * (-len(b64) % 4)
text = base64.b64decode(b64.encode('ascii')).decode('utf-8')
open('scripts/build_all_modules.py', 'a', encoding='utf-8').write(text + '\n')
print('Appended successfully.')
