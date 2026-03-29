from os import system
from requests import get
from threading import Lock
import concurrent.futures

lock = Lock()

# Browser-like headers to avoid being blocked by Instagram's bot detection
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

def check_user(user: str) -> None:
    """
    Check if an Instagram account exists by scraping the public profile page.

    Categorizes results as:
      - exists       : HTTP 200 and no "page isn't available" message
      - not_exists   : HTTP 404 or "Sorry, this page isn't available." in body
      - blocked      : HTTP 429 / other 4xx indicating IP block or captcha
      - network_error: Any exception (timeout, connection error, etc.)
    """
    try:
        url = f"https://www.instagram.com/{user}/"
        response = get(
            url,
            headers=HEADERS,
            proxies=proxies,
            timeout=10,
            allow_redirects=True
        )

        if response.status_code == 200:
            if "Sorry, this page isn't available." in response.text:
                # Page loaded but Instagram shows the "not available" message
                print("[-] User not found =>", user)
                file_name = "not_exists"
            else:
                # Page loaded and content looks like a real profile
                print("[+] Account exists =>", user)
                file_name = "exists"
        elif response.status_code == 404:
            print("[-] User not found =>", user)
            file_name = "not_exists"
        elif response.status_code in (429, 403):
            # Too many requests or forbidden – likely IP blocked or captcha triggered
            print("[-] IP blocked / captcha =>", user)
            file_name = "blocked"
        else:
            print(f"[-] Unexpected status {response.status_code} =>", user)
            file_name = "blocked"
    except Exception:
        print("[-] Network error =>", user)
        file_name = "network_error"

    with lock:
        open(f"output/{file_name}.txt", "a+").write(user + "\n")

if __name__ == '__main__':
    system("cls")
    system("title Instagram Old Account Finder ^| @hiddenexe")

    users = open("data/users.txt", "r", encoding="utf-8").read().splitlines() # email or username list
    proxy = "user:pass@ip:port" # If you do not use a proxy, you will be banned after 100 scans.

    proxies = {'http': proxy, 'https': proxy}
    #proxies = None
    thread_count = 20

    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
        future_to_account = {executor.submit(check_user, user.split(':')[0]): user for user in users}
        for future in concurrent.futures.as_completed(future_to_account):
            try:
                future.result()
            except:
                pass




