import sys
def replace_chars(input):
    # 初始化窗口，用于存储最近出现的10个字符
    window = []
    output = ''

    # 遍历输入字符串的每个字符
    for char in input:
        # 检查字符是否在窗口中
        if char in window:
            # 如果字符已出现在窗口中，则在结果字符串中添加'-'，并将当前元素移到window最后面
            output+= '-'
            window.remove(char)
            window.append(char)
        else:
            # 如果字符未出现在窗口中，则在结果字符串中添加该字符
            output += char
            # 更新窗口,确保窗口最多包含10个字符，若多余，则删除最前面的字符
            window.append(char)
            if len(window) > 10:
                window.pop(0)

    return output

if __name__=="__main__":
    if len(sys.argv) != 2:
        print("使用方式: python3 test2.py str")
        sys.exit(1)
    input=sys.argv[1]
    print(replace_chars(input))