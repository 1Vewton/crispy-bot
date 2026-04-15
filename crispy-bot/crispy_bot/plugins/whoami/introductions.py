from utils import get_random_sentence

# Strings
introduction_normal = (
"""我是QQ群聊天机器人🤖Crispy，由支持向量机谢谢喵（QQ：3438382441）开发～
如果我出现无响应或其他故障，可以联系他帮忙处理喵！

输入「help」可以查看我的功能列表，
"""
)


def get_introduction_normal():
    return introduction_normal + get_random_sentence()

