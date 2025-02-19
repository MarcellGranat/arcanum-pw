import json
import time

def convert_cookie_txt_to_json(txt_file_path: str, json_file_path: str):
    with open(txt_file_path) as file:
        item_names = [
            "name",
            "value",
            "domain",
            "path",
            "expires",
            "httpOnly",
            "secure",
            "sameSite"
        ]

        list_of_cookies = []
        for line in file.readlines():
            cookie_item = {}
            values = line.split("\t")
            for name, value in zip(item_names, values):
                cookie_item[name] = value.strip()
            
            # Convert expires to timestamp if necessary
            if "expires" in cookie_item and cookie_item["expires"]:
                try:
                    cookie_item["expires"] = int(time.mktime(time.strptime(cookie_item["expires"], "%Y-%m-%dT%H:%M:%S.%fZ")))
                except ValueError:
                    pass
            
            # Convert httpOnly and secure to boolean
            cookie_item["httpOnly"] = cookie_item["httpOnly"] == "✓"
            cookie_item["secure"] = cookie_item["secure"] == "✓"
            
            # Ensure sameSite is one of the expected values
            if cookie_item["sameSite"] not in ["Strict", "Lax", "None"]:
                cookie_item["sameSite"] = "None"
            
            list_of_cookies.append(cookie_item)

    with open(json_file_path, "w") as file:
        file.write(json.dumps(list_of_cookies, indent=4))

# Convert the specific file
if __name__ == "__main__":
    import os
    raw_cookies = os.listdir("cookies_raw")

    for cookie in raw_cookies:
        convert_cookie_txt_to_json(f"cookies_raw/{cookie}", f"cookies/{cookie.replace('.txt', '.json')}")