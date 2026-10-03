def prepare_message():
    """准备一条待发送的消息。"""
    message = "明天下午 3 点召开项目会议。"
    print(f"待发送消息：{message}")
    return message


def request_approval(message):
    """等待人工审批，返回审批结果。"""
    print("\n等待人工审批...")
    print(f"待审批内容：{message}")

    approval = input("是否批准发送？(yes/no)：")

    if approval == "yes":
        return True

    return False


def send_message(message):
    """模拟发送消息。"""
    print(f"\n消息已发送：{message}")


def run():
    message = prepare_message()

    approved = request_approval(message)

    if approved:
        send_message(message)
        return "approved"

    print("\n审批被拒绝，消息未发送。")
    return "rejected"


if __name__ == "__main__":
    result = run()
    print(f"\n最终结果：{result}")
