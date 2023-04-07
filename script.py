#Imports
import re
from bs4 import BeautifulSoup
import requests
import os
import pathlib
from time import sleep

## The website base url
base_url = "https://www.imagefap.com"

## Global variables
gallery_url = ""
gallery_path = ""
images = []

def main():
    ask_image_url()
    ask_download_folder_name()
    print("Fetching gallery links...")
    get_image_links()
    print("Downloading gallery")
    download_images()

def ask_image_url():
    """
        Prompts the user for the ImgFap gallery URL
        @returns void
    """
    global gallery_url
    user_input = input("Please insert your gallery url: ")
    matches = re.match(base_url, user_input)

    if(matches == None):
        print("Invalid gallery URL!")
        ask_image_url()

    else: 
        gallery_url = user_input

def ask_download_folder_name():
    """
        Prompts the user for the folder name where the gallery will be stored.
        Notice that every gallery is stored under "Downloads" in the application
        directory.
        @returns Void
    """
    global gallery_path
    download_folder = ""
    user_input = input('Name of the folder you want to download: ')

    parent_folder = pathlib.Path(__file__).parent.resolve()
    download_folder = os.path.join(parent_folder, "downloads", user_input)
    folder_exists = os.path.exists(f"./downloads/{user_input}")
    
    if (folder_exists):
        print("Folder already exists!")
        ask_download_folder_name()
    else:        
        os.makedirs(download_folder)
        gallery_path = download_folder

def get_image_links(link = ""):
    """"
        Used to get the image link from the gallery main page URL. 
        The optional param @link it's used to fetch the data for an
        specific page. If @link it's not set, it will use the gallery
        main page to fetch all the next links.
        @param link : str (Optional)
            The link where the image links search will begin
        @returns void
    """

    if link != "":
        request = requests.get(gallery_url + link)
    else:
        request = requests.get(gallery_url)

    page = BeautifulSoup(request.text, 'html.parser')
    next_button = page.find('a', string=':: next ::')
    
    links = page.select('a[href^="/photo/"]')
    for link in links:
        images.append(base_url + link['href'])

    if (next_button):
        get_image_links(next_button['href'])

def download_images():  
    """
        Download all images stored in the "global" list @images.
        If an error occurs during the image download, the process
        will be aborted and the created folder will be deleted.
        @returns void
    """

    try:
        for index, link in enumerate(images):
            request = requests.get(link)
            page_content = BeautifulSoup(request.text, 'html.parser')
            image = page_content.select('img[src*="/images/full"]')[0]
            image_link = image['src']
            if (image_link):
                image_path = os.path.join(gallery_path, f"{index}.jpeg")
                with open(image_path, "wb") as f:
                    f.write(requests.get(image_link).content)
    except:
        os.rmdir(gallery_path)
        print('Something went wrong... Aborting.')
        sleep(3)
        exit(0)
    
## Calls the main function to run the application
main()