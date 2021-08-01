#!/usr/bin/env python3

import configparser
import os
import sys
from colorama import init, Fore, Style
import shutil
from unrar import rarfile
import pyfiglet

init(autoreset=True)

MOVIE_FILE_TYPES = [".mkv", ".avi", ".mp4"]

def print_banner():

    banner = pyfiglet.figlet_format("XFERER")
    print(banner)
    return


def get_config():
    try:
        cfg = configparser.ConfigParser()
        cfg.read("config.ini")
        locations = (
            cfg.get("directories", "movies_dir"),
            cfg.get("directories", "torrents_dir"),
        )

    except configparser.NoSectionError:
        print("no config file found!")
        print("Creating new config file...")
        movies_dir = input("Please enter the movies directory: ")
        torrents_dir = input("Please enter the torrents directory: ")
        cfg_ini = open("config.ini", "w+")
        cfg_ini.write("[directories]\n")
        cfg_ini.write("movies_dir = %s\n" % movies_dir)
        cfg_ini.write("torrents_dir = %s\n" % torrents_dir)
        print("Please rerun program")
        sys.exit(-1)

    return locations


def pos_print(text: str):
    """
    :param text: function to print a green plus sign in brackets if the outcome
    of whatever code is favorable
    """
    print(Fore.GREEN + "[+] " + Style.RESET_ALL + text)
    return


def neg_print(text: str):
    """
    :param text: function to print a red minus sign in brackets if the outcome
    of whatever code is not favorable
    """
    print(Fore.RED + "[-] " + Style.RESET_ALL + text)
    return


def print_dir(directory_list):
    print("\nDirectory Listing:\n")
    for directory_entry in directory_list:
        print(
            str(directory_list.index(directory_entry) + 1)
            + ": "
            + directory_entry
        )
    return

def make_movie_dir(new_directory_name):
    try:
        path = os.path.join(movies_dir, new_directory_name)
        os.mkdir(path)
        pos_print(path + " created!")
    except FileExistsError:
        neg_print("directory already exists!")


def unrar_movie(movie_to_unrar: str):
    try:
        rar = rarfile.RarFile(movie_to_unrar)
        rar.extractall()
        pos_print("Successfully extracted!")

    except Exception as e:
        print(e)
        neg_print("Exception has occurred!")


def copy_movie(orig_movie_name: str, new_file_name: str):
    try:
        shutil.copy2(orig_movie_name, movies_dir + "/" + new_file_name)
        pos_print("Movie copied!")

    except:
        neg_print("An error has occurred during copying!")


def rename_movie(original_name: str, new_dir_and_file_name: str):
    try:
        os.rename(
            movies_dir + "/" + new_dir_and_file_name + "/" + original_name,
            movies_dir
            + "/"
            + new_dir_and_file_name
            + "/"
            + new_dir_and_file_name
            + ".mkv",
        )
        pos_print("File has been renamed")
    except FileExistsError:
        neg_print("Directory/File already exists!")


def process(k, v):
    if os.path.isdir(k):
        os.chdir(k)
        new_dir_list = os.listdir()

        for file_or_dir in new_dir_list:
            file_extension = os.path.splitext(file_or_dir)[1]
            if file_extension in MOVIE_FILE_TYPES:
                make_movie_dir(v)
                copy_movie(file_or_dir, v)
                rename_movie(file_or_dir, v)
                os.chdir("../")

            elif file_extension == ".rar":
                unrar_movie(file_or_dir)
                make_movie_dir(v)
                copy_movie(file_or_dir, v)
                rename_movie(file_or_dir, v)
                os.chdir("../")

    file_name, file_extension = os.path.splitext(k)
    if file_extension == ".rar":
        unrar_movie(k)

    else:
        file_name, file_extension = os.path.splitext(k)
        if file_extension in MOVIE_FILE_TYPES:
            make_movie_dir(v)
            copy_movie(k, v)
            rename_movie(k, v)


if __name__ == "__main__":
    print_banner()
    cfg = get_config()

    movies_dir = cfg[0]
    torrents_dir = cfg[1]

    os.chdir(torrents_dir)
    directory_list = os.listdir()
    print_dir(directory_list)

    # this is the dictionary we store our items to be processed
    to_be_processed = {}

    while True:
        selection = input(
            Fore.CYAN
            + "\nOptions:\n\n1: Type the entry number to add entry to processing queue.\n2: Type 'p' to process queue.\n3: Type 'l' to reprint the list.\n4: Type 'd' to delete an entry\n\nYour Choice: "
        ).lower()

        if selection == "q":
            pos_print("\nThank you and goodbye!")
            sys.exit()

        if selection == "p":
            break

        if selection == "l":
            print_dir(directory_list)

        else:
            try:
                file_or_dir = directory_list[int(selection) - 1]
                pos_print(f"----> You chose: {file_or_dir}\n")

                to_be_processed[file_or_dir] = input(
                    "\nPleae type new file name: "
                )

                pos_print(
                    directory_list[int(selection) - 1]
                    + " was added to the queue!\n"
                )

            except Exception as e:
                neg_print("Error")

        pos_print("----> The current queue is:\n")
        for k, v in to_be_processed.items():
            print(k + " ------> " + v)

    pos_print("Processing!")

    # TODO: Thread and process
    for k, v in to_be_processed.items():
        process(k, v)
