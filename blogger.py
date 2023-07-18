import requests
from bs4 import BeautifulSoup
import signal
import sys
import time
from pwn import *
import pdb
import re

def handler(sig, frame):
    print("\n\n[!] Saliendo...\n")
    sys.exit(1)

# Flujo de signal / CTRL +C
signal.signal(signal.SIGINT, handler)

def get_blog_info(u):
    murl = f"https://{u}.blogspot.com/"
    author = requests.get(murl)
    soupm = BeautifulSoup(author.text, 'html.parser')
    link_tag = soupm.find('link', rel='me')
    if link_tag:
      blog = link_tag.get('href').strip()
      return blog, soupm
    return None, None

def get_author_info(blog):
    if not blog:
        print("El enlace a Blogger no está disponible. No se puede obtener la información del autor.")
        return None, None

    binfo = requests.get(blog)
    soupn = BeautifulSoup(binfo.text, 'html.parser')
    nameb = soupn.find('h1')
    dateb = soupn.findAll('p', class_='sidebar-item item-key')
    mail = soupn.find('a', class_='email')
    blogs = soupn.find_all('a', target='null')
    imgb = soupn.find('img', class_='photo')
    locab = soupn.find('span', class_='locality')
    regionb = soupn.find('span', class_='region')
    countryb = soupn.find('span', class_='country')
    interests = soupn.find('span', class_='favorites')
    about = soupn.find('span', class_='title')
    role = soupn.find('span', class_='role')

    if mail:
      correod = mail['href']
      correo = correod.replace("mailto:", "")
      print("Correo:", correo)
    else:
      pass

    if blogs:
      print("Blogs:")
      for blog in blogs:
         urlb = blog['href']
         print(urlb)
    else:
      pass

    if imgb:
      src = imgb['src']
      print("Foto:", src)
    else:
      pass

    if locab:
      print("Localizacion:", locab.text.strip(), regionb.text.strip(), countryb)
    else:
      pass

    if interests:
      print("Intereses:", interests.text.strip())
    else:
      pass

    if role:
      print("Rol:", role.text.strip())
    else:
      pass

    if about:
      print("Otros:", about.text.strip())
    else:
      pass

    return nameb, dateb

def get_post_info(url):
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, 'html.parser')

    posts = soup.find_all('h3', class_='post-title entry-title')
    dates = soup.find_all('h2', class_='date-header')
    timestamps = soup.find_all('abbr', class_='published')
    timestamps2 = soup.find_all('time', class_='published')
    authors = soup.find_all('span', itemprop='name')
    authors2 = soup.find_all('span', class_='fn')
    authors3 = soup.find_all('span', class_='meta_author')
    authors_extra = soup.find_all('a', class_='profile-name-link g-profile')

    return posts, dates, timestamps, timestamps2, authors, authors2, authors3, authors_extra

def print_info(posts, dates, timestamps, timestamps2, authors, authors2, authors3, authors_extra, nameb, dateb):
    print("\n")
    if posts:
        print("Primera publicación:", posts[-1].text.strip())
    else:
        pass

    if dates:
        print("Fecha de publicación:", dates[-1].text.strip())
    else:
        pass

    if timestamps:
        print("Timestamp:", timestamps[-1].text.strip())
    elif timestamps2:
        print("Timestamp:", timestamps2[-1].text.strip())
    else:
        pass

    if authors:
        print("Autor:", authors[-1].text.strip())
    elif authors2:
        print("Autor:", authors2[-1].text.strip())
    elif authors3:
        print("Autor:", authors3[-1].text.strip())
    else:
        pass

    if authors_extra:
        print("Nombre en Blogger:", authors_extra[-1].text.strip())
    elif nameb:
        print("Nombre en Blogger:", nameb.text.strip())
    else:
        pass

    if dateb:
     for date in dateb:
          datel = date.text.strip()
          if re.match("^En", datel):
           t = datel.replace("En Blogger desde", "")
           dateg = t.replace("\n", "")
           print("Fecha de creacion Blogger:", dateg)
          else:
           pass
    else:
        pass

def check(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    ex = soup.find('div', class_='status-msg-body')
    if response.status_code == 200:
        content = response.text
        if not ex:
            return True
    return False

def main():
    u = input("Blog: ").strip()

    p0 = log.progress("Perfil en Blogger")
    p0.status("Buscando Blogger...")
    print("\n")

    blog, soupm = get_blog_info(u)
    if blog or u:
        p0.status(blog)

        nameb, dateb = get_author_info(blog)
        print("\n")
        p1 = log.progress("Año")
        p1.status("Buscando año...")

        time.sleep(2)

        p2 = log.progress("Mes")
        p2.status("Buscando mes...")

        for year in range(2000, 2024):
            url = f"https://{u}.blogspot.com/{year}"
            p1.status(url)
            if check(url):
                for month in range(1, 13):
                    month_str = str(month).zfill(2)
                    url = f"https://{u}.blogspot.com/{year}/{month_str}"
                    p2.status(url)
                    if check(url):
                        posts, dates, timestamps, timestamps2, authors, authors2, authors3, authors_extra = get_post_info(url)
                        print_info(posts, dates, timestamps, timestamps2, authors, authors2, authors3, authors_extra, nameb, dateb)
                        break
                break

if __name__ == "__main__":
    main()
