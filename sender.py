import socket
import keyboard

PORT = 50007

# 簡報筆常見的翻頁按鍵名稱
TARGET_KEYS = ['page down', 'page up', 'space', 'right', 'left', 'up', 'down']

CLIENT_IP = ""
sock = None


def ask_client_ip():
    print("=== 主電腦控制端 ===")
    print("每次啟動都要輸入副電腦（接收端）的 IP，不用再改程式。")
    while True:
        ip = input("請輸入副電腦 IP 地址: ").strip()
        parts = ip.split(".")
        if (
            len(parts) == 4
            and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)
        ):
            return ip
        print("IP 格式不正確（例如 192.168.1.20），請再輸入一次。")


def on_key_event(e):
    # 當按鍵被按下且符合簡報筆按鍵時
    if e.event_type == keyboard.KEY_DOWN and e.name in TARGET_KEYS:
        try:
            sock.sendto(e.name.encode("utf-8"), (CLIENT_IP, PORT))
            print(f"[{e.name}] 已同步發送到副電腦")
        except Exception as ex:
            print(f"發送失敗: {ex}")


def main():
    global CLIENT_IP, sock
    CLIENT_IP = ask_client_ip()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("=== 主電腦控制端已啟動 ===")
    print(f"正在監聽簡報筆按鍵，準備同步至: {CLIENT_IP}")
    print("按 Ctrl+C 可結束程式。")

    keyboard.hook(on_key_event)
    keyboard.wait()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已結束。")
    except Exception as ex:
        print(f"程式錯誤: {ex}")
        input("按 Enter 關閉...")
