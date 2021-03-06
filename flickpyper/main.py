from flickrapi import FlickrAPI, FlickrError

from os import environ, path, remove, system
import sys
from flickpyper.config import *

flickr = FlickrAPI(API_KEY, '', format='parsed-json')
options = None

from flickpyper.options import parse_opts
from flickpyper.common import os, save_file, get_default_image_path
from flickpyper.winmac import set_wallpaper_windows, set_wallpaper_macosx
from flickpyper.linux import set_wallpaper_linux
from flickpyper.pickles import put_ids, get_ids

def set_wallpaper(path):
    _os = os()
    if _os=='windows':
        print("OS - Windows")
        set_wallpaper_windows(path)
    elif _os=='macosx':
        print("OS - Mac")
        set_wallpaper_macosx(path)
    elif _os in ('linux', 'unix'):
        print("OS - Unix")
        set_wallpaper_linux(path)
    else:
        print("Unsupported machine")
        return False
    return True

def run():
    options = parse_opts(sys.argv[1:])
    if options.verbose: print("OS: {}".format(os()))

    size_idx = SIZES.index(options.size)
    if not size_idx or size_idx < 0:
        print(f"Invalid size argument: {options['size']}.\
                  \nPlease select from: {', '.join(SIZES)}.")
        sys.exit(1)

    opts = {k:v for (k,v) in vars(options).items() if k in ('page','per_page','date') and v}
    if options.verbose: print(f"Getting interesting list: {opts}")
    try:
        list = flickr.interestingness.getList(**opts)['photos']['photo']
    except FlickrError as e:
        print(f"Flickr API error: {e.code}")
        sys.exit(1)

    try:
        # TODO: just randomize instead of dump
        ids = get_ids(options.dump)
    except:
        # That's ok, file from Ruby version
        ids = []
    if options.verbose: print(f"Used Ids: {ids}")
    list = [p for p in list if p['id'] not in ids]
    if options.verbose: print(f"Filtered: {list[:3]}...")

    idx = None
    url = None

    if options.verbose: print("Selecting large photo")
    for i in range(len(list)):
        try:
            size = flickr.photos.getSizes(photo_id=list[i]['id'])['sizes']['size']
        except FlickrError as e:
            print(f"Flickr API error: {e.code}")
            sys.exit(1)
        if options.verbose: print(f"size = {size[0]}...")
        def detect(s):
            my_size_idx = SIZES.index(s['label'])
            return my_size_idx and my_size_idx >= size_idx
        try:
            my_size = next(filter(detect, size))
        except StopIteration:
            my_size = None
        if my_size is not None:
            idx = i
            url = my_size['source']
            if options.verbose: print(f"url = {url}")
            break

    if idx is not None:
        my_photo = list[idx]

        if options.verbose: print("Saving picture")
        save_file(url, options.image)
        if options.verbose: print("Setting wallpaper")
        result = set_wallpaper(options.image)
        if result:
            if options.verbose: print(f"Set photo {my_photo['id']} as wallpaper")
            ids.append(my_photo['id'])
            put_ids(options.dump, ids)
        else:
            print(f"Unable to set photo {my_photo['id']} as wallpaper")
    else:
        print("Unable to find photo for wallpaper")

if __name__=='__main__':
    run()
