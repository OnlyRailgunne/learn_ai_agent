def prepare_message():
    message = "明天下午 3 点召开项目会议。"

    print(f"准备发送消息：{message}")

    return message


def start():
    message = prepare_message()

    approval_request = {
        "status": "waiting_approval",
        "message": message,
    }

    print("\nAgent 已暂停，等待人工审批。")

    return approval_request


def send_message(message):
    print(f"\n消息已发送：{message}")


def resume(approval_request, approved):
    message = approval_request["message"]

    if approved:
        send_message(message)

        return {
            "status": "completed",
            "message": message,
        }

    print("\n审批被拒绝，消息未发送。")

    return {
        "status": "rejected",
        "message": message,
    }


if __name__ == "__main__":
    # 第一阶段：启动 Agent
    approval_request = start()

    print("\n=== Approval Request ===")
    print(approval_request)

    # 第二阶段：人工做出决定
    answer = input("\n是否批准？(yes/no)：")

    approved = answer == "yes"

    # 第三阶段：恢复 Agent
    result = resume(
        approval_request,
        approved=approved,
    )

    print("\n=== Final Result ===")
    print(result)