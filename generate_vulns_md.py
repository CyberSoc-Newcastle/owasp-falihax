#!/usr/bin/env python3

"""
generate_vulns_md.py
=======================
Generates a VULNS.md markdown document from a vulns.json file.

Copyright CyberSoc (c) October 2022.
"""

import json
import requests
from urllib.parse import urljoin
import os

# which code file extensions map to which github markdown highlighter?
markdown_highlighting = {".py" : "python"}

class XKCD():

    def __init__(self, num: int):
        r = requests.get(f"https://xkcd.com/{num}/info.0.json")
        j = json.loads(r.text)
        self.__num: int = j["num"]
        self.__img: str = j["img"]
        self.__title: str = j["safe_title"]
        self.__alt: str = j["alt"]

    def __repr__(self) -> str:
        return f"<XKCD {self.num}: \"{self.title}\" {self.url}>"

    def __str__(self) -> str:
        return self.alt

    @property
    def num(self) -> int:
        return self.__num

    @property
    def img(self) -> str:
        return self.__img

    @property
    def title(self) -> str:
        return self.__title
    
    @property
    def alt(self) -> str:
        return self.__alt

    @property
    def url(self) -> str:
        return f"https://xkcd.com/{self.num}/"

def fetch_vulns_json() -> dict:
    f = open('vulns.json')
    j = json.loads(f.read())
    f.close()
    return j

next_misc_qualifier = 1

def get_misc_qualifier() -> str:
    global next_misc_qualifier
    qualifier = f"B{str(next_misc_qualifier).zfill(2)}"
    next_misc_qualifier += 1
    return qualifier

def render_category(category: dict, repo=None) -> dict:
    output = ""
    category_qualifier = ""
    category_qualifier_text = ""
    headings = []
    if 'owasp-id' in category:
        category_qualifier = category['owasp-id']
        category_qualifier_text = f"OWASP {category_qualifier}"
    else:
        category_qualifier = get_misc_qualifier()
        category_qualifier_text = category_qualifier
    category_heading = f"{category_qualifier_text}: {category['name']}"
    if 'link' in category:
        output += f"## [{category_heading}]({category['link']})\n"
    else:
        output += f"## {category_heading}\n"
    output += f"{category['description']}\n\n"
    
    # process instances
    if category['instances']:
        for qualifier_num, instance in enumerate(category['instances'], start=1):
            instance_qualifier = f"{category_qualifier}-{str(qualifier_num).zfill(2)}"
            if 'link' in instance:
                output += f"### [{instance_qualifier}: {instance['name']}]({instance['link']})\n"
            else:
                output += f"### {instance_qualifier}: {instance['name']}\n"
            headings.append(f"{instance_qualifier}: {instance['name']}")
            if 'xkcd' in instance:
                xkcd = XKCD(instance['xkcd'])
                output += f"[![XKCD {xkcd.num}: \"{xkcd.title}\"]({xkcd.img})]({xkcd.url})\n"
                output += f"> *{xkcd.alt}*\n\n"
            output += f"{instance['description']}\n\n"
            if 'examples' in instance and instance['examples'] and repo:
                output += f"#### Examples\n"
                for example in instance['examples']:
                    example_url = urljoin(urljoin("https://github.com", repo+"/", allow_fragments=False), f"blob/{example['at_commit']}/{example['file']}", allow_fragments=False)
                    file_raw_url = urljoin(urljoin("https://raw.githubusercontent.com", repo+"/", allow_fragments=False), f"{example['at_commit']}/{example['file']}", allow_fragments=False)
                    file_raw_lines = requests.get(file_raw_url).text.split("\n")

                    highlighter = ""
                    for ext, name in markdown_highlighting.items():
                        if example['file'].endswith(ext):
                            highlighter = name
                            break
                        
                    for line in example['lines']:
                        lines_raw = ""
                        if '-' in line:
                            # multi-line
                            start_line = int(line.split('-')[0])
                            end_line = int(line.split('-')[1])
                            example_lines_url = urljoin(urljoin("https://github.com", repo+"/", allow_fragments=False), f"blob/{example['at_commit']}/{example['file']}#L{start_line}-L{end_line}", allow_fragments=True)
                            lines_raw = "\n".join(file_raw_lines[start_line-1:end_line])
                            output += f"*In [{example['file']}]({example_url}), lines [{line}]({example_lines_url}):*\n"
                        else:
                            # single-line
                            example_lines_url = urljoin(urljoin("https://github.com", repo+"/", allow_fragments=False), f"blob/{example['at_commit']}/{example['file']}#L{line}", allow_fragments=True)
                            lines_raw = file_raw_lines[int(line)-1]
                            output += f"*In [{example['file']}]({example_url}), line [{line}]({example_lines_url}):*\n"
                        output += f"```{highlighter}\n"
                        output += f"{lines_raw}\n"
                        output += f"```\n"
                        
            if 'link' in instance['solution']:
                output += f"#### [Solution]({instance['solution']['link']})\n"
            else:
                output += f"#### Solution\n"
            if 'xkcd' in instance['solution']:
                xkcd = XKCD(instance['solution']['xkcd'])
                output += f"[![XKCD {xkcd.num}: \"{xkcd.title}\"]({xkcd.img})]({xkcd.url})\n"
                output += f"> *{xkcd.alt}*\n\n"
            output += f"{instance['solution']['description']}\n"
    else:
        output += f"*There are no known vulnerabilities in this category.*\n"
    
    return {'output': output, 'root_heading': category_heading, 'headings': headings}

def anchorise(heading: str) -> str:
    return heading.lower().replace(" ", "-").replace(":", "").replace("\"", "").replace("(", "").replace(")", "")

if __name__ == '__main__':
    vulns = fetch_vulns_json()
    output = f"\n[comment]: # (Generated from JSON file by {os.path.basename(__file__)})\n"
    output += "[comment]: # (Intended to be read in GitHub's markdown renderer. Apologies if the plaintext formatting is messy.)\n\n"
    output += "# OWASP Falihax Vulnerabilities\n"
    output += "*General hackathon feedback by [CyberSoc](https://cybersoc.org.uk/?r=falihax-vulns)*\n\n"
    output += "A list of known vulnerabilites in the OWASP \"Falihax\" hackathon web app. This is a collection of vulnerabilities found by those who took part and some that noone found! "
    output += "This list isn't exhaustive - if you find more vulnerabilites then let us know and we'll add them to this list!\n\n"
    output += "This is general feedback - for your specific feedback and points total, see your own repository!\n\n"
    output += "## Table of Contents\n"
    rendered = list(render_category(category, repo=vulns["repo"]) for category in vulns["categories"])
    for category in rendered:
        output += f"* [{category['root_heading']}](#{anchorise(category['root_heading'])})\n"
        for heading in category['headings']:
            output += f"    - [{heading}](#{anchorise(heading)})\n"
    output += "\n\n"
    output += "\n".join(category['output'] for category in rendered)
    f = open('VULNS.md', 'w')
    f.write(output)
    f.close()
    print("Done.")
