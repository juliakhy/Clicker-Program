import socket
import sys
import keyboard

PORT = 50007
_stop = False
_console_handler = None


def request_stop():
    global _stop
    _stop = True


def install_stop_handler():
    """讓 Windows 主控台的 Ctrl+C 可以打斷正在等待封包的程式。"""
    global _console_handler
    if sys.platform != "win32":
        return

    import ctypes
    from ctypes import wintypes

    handler_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.DWORD)

    def handle_console_ctrl(ctrl_type):
        # 0 = Ctrl+C，1 = Ctrl+Break
        if ctrl_type in (0, 1):
            request_stop()
            return True
        return False

    _console_handler = handler_type(handle_console_ctrl)
    ctypes.windll.kernel32.SetConsoleCtrlHandler(_console_handler, True)


def local_ips():
    ips = set()
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ips.add(info[4][0])
    except OSError:
        pass
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        probe.connect(("8.8.8.8", 80))
        ips.add(probe.getsockname()[0])
        probe.close()
    except OSError:
        pass
    ips.discard("127.0.0.1")
    return sorted(ips)


def main():
    install_stop_handler()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 綁定所有介面，監聽指定 Port
    sock.bind(("", PORT))
    # 定期醒來，這樣 Ctrl+C 才不會被一直卡住的接收動作吃掉
    sock.settimeout(0.5)

    print("=== 副電腦接收端已啟動 ===", flush=True)
    found = local_ips()
    if found:
        print("請在主電腦輸入以下其中一個 IP：", flush=True)
        for ip in found:
            print(f"  {ip}", flush=True)
    print(f"正在監聽 Port {PORT} 的同步訊號...", flush=True)
    print("按 Ctrl+C 可結束程式。", flush=True)

    try:
        while not _stop:
            try:
                data, addr = sock.recvfrom(1024)
            except socket.timeout:
                continue
            except OSError:
                if _stop:
                    break
                raise

            key_name = data.decode("utf-8")
            print(f"收到來自 {addr[0]} 的指令 -> 模擬按鍵: {key_name}", flush=True)

            # 在副電腦上模擬按下對應的按鍵（觸發 PowerPoint 翻頁）
            keyboard.send(key_name)
    finally:
        sock.close()

    print("\n已結束。", flush=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已結束。", flush=True)
    except Exception as ex:
        print(f"程式錯誤: {ex}", flush=True)
        try:
            input("按 Enter 關閉...")
        except EOFError:
            pass
