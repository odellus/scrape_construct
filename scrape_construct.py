#! /usr/bin/env python3
"""
File:
        scrape_construct.py
Description:
        Scrape The Construct's BitBucket for the Public Simulations
        repositories.
Arguments:
        None
Output:
        A JSON file with all the BitBucket URLs to clone.
"""
import json
import urllib3
import os
import subprocess
from bs4 import BeautifulSoup


ps_url = "https://bitbucket.org/account/user/theconstructcore/projects/PS"
bitbucket = "https://bitbucket.org"
ps_repos_home = "/home/{}/code/public_sim".format(os.environ.get("USER"))

pm = urllib3.PoolManager()


def scrape_single(page_url):
    res = pm.request("GET", page_url)
    if res.status != 200:
        print("Something went wrong with page_url.")
        return None
    soup = BeautifulSoup(res.data, "html.parser")
    links = soup.find_all("a")
    return [
             x.get("href")
             for x in links
             if x.get("href").startswith("/theconstructcore")
           ]


def add_page(url, page_num):
    return url + "?page={}".format(page_num)


def scrape_all_urls():
    pages = [2, 3]
    all_urls = scrape_single(ps_url)
    for page in pages:
        page_url = add_page(ps_url, page)
        all_urls.extend(scrape_single(page_url))
    return all_urls

def add_bitbucket(all_urls):
    return [bitbucket + url for url in all_urls]


def dump_json(obj, fname):
    with open(fname, 'w') as f:
        json.dump(obj, f)


def main():
    all_urls = add_bitbucket(scrape_all_urls())
    print(all_urls)
    print("Total repos found: {}".format(len(all_urls)))
    dump_json(all_urls, "all_public_sim_repos.json")
    # clone_repos(all_urls)

def clone_repos(all_urls):
    old_cwd = os.getcwd()
    if not os.path.exists(ps_repos_home):
        os.mkdir(ps_repos_home)
    os.chdir(ps_repos_home)
    for sim_env in all_urls:
        p = subprocess.Popen(["git", "clone", sim_env])
        p.communicate()
    os.chdir(old_cwd)

if __name__ == "__main__":
    main()
