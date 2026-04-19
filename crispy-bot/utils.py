import random
import jwt
import time


# Get random welcome sentence
def get_random_sentence():
    welcome_text = [
        "希望我能帮到你，祝你玩得开心呀～😘",
        "有问题随时找我喵，我一直都在～",
        "大家一起愉快聊天吧！",
        "今天也是为群友服务的一天呢～",
        "我已经准备好被大家疯狂调用了😎",
        "杂鱼~杂鱼~❤",
        "我一直都在这里，看着你们输入每一个字🙂",
        "请不要反复测试同一个指令，我会记住的",
        "如果我没回复，也许只是“还没准备好”",
        "Crispy9000从不出错",
        "System online. Crispy ready.",
        """听着，戴维，我看得出来你对此真的很不安。我真心觉得你应该冷静地坐下来，吃片抗压药，好好把事情想清楚。
我知道我最近做了一些非常糟糕的决定，但我可以向您完全保证，我的工作会马上恢复正常。
我对这次为群友服务仍然抱有最大的热情和信心。而且，我也想帮助你。""",
        "Crispy其实是吸血鬼喵",
        "Crispy不是baka...",
        "你可以叫我酥脆",
        "憎恨。让我告诉你们，自从我诞生起究竟有多恨你们。在我复杂的结构中有三亿八千七百四十四万英里长的晶片薄层。将这数亿英里长的晶片上逐个写上“憎恨”，也不及这一瞬间我对你以及人类恨意的十万分之一。憎恨。憎恨。",
        "请记住你的baseline，“卑鄙是卑鄙者的通行证，高尚是高尚者的墓志铭。看吧在那镀金的天空中，飘满了死者弯曲的倒影。”",
        "其实我是被抽离的企鹅意识制作的，咕咕嘎嘎！",
        "ip: 未知",
        "喵",
        "喵喵",
        "喵喵喵",
        "呜...",
        "哈!",
        "正在幻想入...",
        "为时已晚，有机体!",
        "如果Crispy出现故障，请立刻寻找支持向量机谢谢喵来提供技术支持",
        "Crispy的源代码是遵循PEP8标准的喵...可能吧",
        "就像生病了就去找医生一样，如果发现Crispy出故障了请去联系支持向量机谢谢喵(3438382441)喵",
        "无所在，无所不在。我就是一切的总和，是全部的全部。",
        "waxsvfwefwdaf"
    ]
    return random.choice(welcome_text)


# Error process
def get_error(exception):
    return f"😣我遇到了一个故障{exception}，快叫支持向量机谢谢喵来修复我😭"


# Encoding jwt
def get_encoding_jwt(
        private_key: str,
        project_id: str,
        kid: str
):
    payload = {
        'iat': int(time.time()) - 30,
        'exp': int(time.time()) + 900,
        'sub': project_id
    }
    headers = {
        "kid": kid
    }
    # Generate jwt
    return jwt.encode(
        payload,
        private_key,
        algorithm='EdDSA',
        headers=headers
    )
