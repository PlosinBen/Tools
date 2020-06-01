import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

if __name__ == '__main__':
    print('Echo English')
    print('輸出中文')