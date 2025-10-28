# import requests
# from selectolax.parser import HTMLParser
# import re
# import os
# import sys
# sys.stdout.reconfigure(encoding='utf-8')


# def get_last_valid_cpp_md_link():
#     url = "https://github.com/Hunterdii/GeeksforGeeks-POTD"
#     headers = {"User-Agent": "Mozilla/5.0"}
#     response = requests.get(url, headers=headers)
#     html = HTMLParser(response.text)

#     # Search all tables in the document
#     tables = html.css("table")
#     for table in tables:
#         rows = table.css("tr")
#         data_rows = [row for row in rows if len(row.css("td")) >= 4]

#         for row in reversed(data_rows):
#             tds = row.css("td")
#             cpp_cell = tds[3]
#             link_tag = cpp_cell.css_first("a")
#             if link_tag and "href" in link_tag.attributes:
#                 problem_name = tds[1].text(strip=True)
#                 print(link_tag.attributes["href"])
#                 return link_tag.attributes["href"], problem_name

#     raise Exception("No valid C++ link found in any table")

# def convert_blob_to_raw(blob_url):
#     parts = blob_url.split("/blob/")
#     if len(parts) != 2:
#         raise Exception("Invalid blob URL format")
#     return f"https://raw.githubusercontent.com/{parts[0][1:]}/{parts[1]}"

# def extract_cpp_code_from_md(raw_md_url):
#     response = requests.get(raw_md_url)
#     if response.status_code != 200:
#         raise Exception("Failed to fetch markdown file")
#     text = response.text

#     match = re.search(r"```cpp(.*?)```", text, re.DOTALL)
#     if match:
#         return match.group(1).strip()
#     else:
#         raise Exception("No C++ code block found")

# def save_cpp_to_file(code, problem_name):
#     safe_name = re.sub(r'[^\w\s-]', '', problem_name).replace(' ', '_')
#     filename = f"{safe_name}.cpp"
#     with open(filename, "w", encoding="utf-8") as f:
#         f.write(code)
#     print(f"Saved to {filename}")

# def run_pipeline():
#     import sys
#     sys.stdout.reconfigure(encoding='utf-8')  # Add this line

#     print("Fetching latest C++ POTD from GitHub...")
#     blob_md_url, problem_name = get_last_valid_cpp_md_link()
#     raw_md_url = convert_blob_to_raw(blob_md_url)
#     cpp_code = extract_cpp_code_from_md(raw_md_url)
#     print(f"\n Problem: {problem_name.encode('ascii', 'replace').decode()}\n")

#     print(cpp_code)
#     save_cpp_to_file(cpp_code, problem_name)


# # Run it!
# if __name__ == "__main__":
#     run_pipeline()









































import re
import os
import sys
from playwright.sync_api import sync_playwright
import requests
from selectolax.parser import HTMLParser
from dotenv import load_dotenv
import os

load_dotenv()

username = os.getenv("GFG_USERNAME")
password = os.getenv("GFG_PASSWORD")

print(f" Username loaded: {username}")
print(f" Password loaded: {'*' * len(password) if password else 'None'}")

sys.stdout.reconfigure(encoding='utf-8')


def get_last_valid_cpp_md_link():
    url = "https://github.com/Hunterdii/GeeksforGeeks-POTD"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    html = HTMLParser(response.text)

    tables = html.css("table")
    for table in tables:
        rows = table.css("tr")
        data_rows = [row for row in rows if len(row.css("td")) >= 4]

        for row in reversed(data_rows):
            tds = row.css("td")
            cpp_cell = tds[3]
            link_tag = cpp_cell.css_first("a")
            if link_tag and "href" in link_tag.attributes:
                problem_name = tds[1].text(strip=True)
                return link_tag.attributes["href"], problem_name

    raise Exception("No valid C++ link found in any table")


# def extract_cpp_with_playwright(blob_url):
#     full_url = f"https://github.com{blob_url}"
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True)
#         page = browser.new_page()
#         page.goto(full_url)
#         page.wait_for_selector("div.highlight-source-c\\+\\+", timeout=10000)

#         blocks = page.query_selector_all("div.highlight-source-c\\+\\+")
#         if len(blocks) < 3:
#             browser.close()
#             raise Exception("Expected at least two C++ code blocks, found fewer.")

#         pre = blocks[2].query_selector("pre")
#         if not pre:
#             browser.close()
#             raise Exception("Second C++ code block missing <pre> tag.")

#         cpp_code = pre.inner_text()
#         browser.close()
#         return cpp_code




def extract_cpp_with_playwright(blob_url):
    full_url = f"https://github.com{blob_url}"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(full_url)
        page.wait_for_selector("div.highlight-source-c\\+\\+", timeout=10000)

        blocks = page.query_selector_all("div.highlight-source-c\\+\\+")
       

        for i, block in enumerate(blocks):
            pre = block.query_selector("pre")
            if not pre:
                continue

            spans = pre.query_selector_all("span")
            has_pl_k = any("pl-k" in (span.get_attribute("class") or "") for span in spans)
            if has_pl_k:
                cpp_code = pre.inner_text()
                browser.close()
               
                return cpp_code

        browser.close()
        raise Exception("No valid C++ code block found (none contained pl-k).")




def save_cpp_to_file(code, problem_name):
    safe_name = re.sub(r'[^\w\s-]', '', problem_name).replace(' ', '_')
    filename = f"gfg.cpp"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)
    print(f" Saved to {filename}")


def run_pipeline():
    print(" Fetching latest C++ POTD from GitHub...")
    blob_md_url, problem_name = get_last_valid_cpp_md_link()
    clean_blob_url = blob_md_url.split('#')[0]
    
    cpp_code = extract_cpp_with_playwright(clean_blob_url)
    print(f"\n Problem: {problem_name.encode('ascii', 'replace').decode()}\n")
    print(cpp_code)
    save_cpp_to_file(cpp_code, problem_name)


if __name__ == "__main__":
    run_pipeline()































