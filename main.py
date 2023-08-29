import time
import instaloader
import os
import shutil
from datetime import datetime


def organise_file(user_name):
    for file in os.listdir(user_name):
        file_path = os.path.join(user_name, file)
        if os.path.isfile(file_path):
            if file.endswith(".jpg"):
                os.makedirs(f"{user_name}/photos", exist_ok=True)
                shutil.move(f"{user_name}/{file}", f"{user_name}/photos/{file}")
            elif file.endswith(".mp4"):
                os.makedirs(f"{user_name}/videos", exist_ok=True)
                shutil.move(f"{user_name}/{file}", f"{user_name}/videos/{file}")
            else:
                os.makedirs(f"{user_name}/others", exist_ok=True)
                shutil.move(f"{user_name}/{file}", f"{user_name}/others/{file}")


def download_post(posts, username, loader):
    for i, post in enumerate(posts):
        if i > 0 and i % 100 == 0:
            print("sleeping for 1 minute")
            time.sleep(60)
        else:
            try:
                loader.download_post(post, target=username)
            except Exception as e:
                print(f"An error occurred at post: {i}")
                print(f"Error: {e}")
    organise_file(username)


def download_new_post(file_list, posts, username, loader):
    # current_date_time = datetime.now()

    last_post_date = max([date.replace('-0', '-') for date in [i.split('_')[0] for i in file_list]],
                         key=lambda x: datetime.strptime(x, '%Y-%m-%d'))
    since = datetime.strptime(last_post_date, "%Y-%m-%d")
    # until = current_date_time.replace(hour=0, minute=0, second=0, microsecond=0)

    filtered_posts = [post for post in posts if post.date > since]
    if filtered_posts:
        download_post(filtered_posts, username, loader)
    else:
        print("No New Post Found")


def download(user_profile, loader):
    username = user_profile.username
    posts = user_profile.get_posts()
    # posts_count = int(user_profile.mediacount)

    user_root_folder = username
    photos_folder = os.path.join(user_root_folder, "photos")
    videos_folder = os.path.join(user_root_folder, "videos")

    if os.path.exists(photos_folder) and os.path.exists(videos_folder):
        file_list = os.listdir(photos_folder) + os.listdir(videos_folder)
        download_new_post(file_list, posts, username, loader)
    elif os.path.exists(photos_folder):
        file_list = os.listdir(photos_folder)
        download_new_post(file_list, posts, username, loader)
    elif os.path.exists(videos_folder):
        file_list = os.listdir(videos_folder)
        download_new_post(file_list, posts, username, loader)
    else:
        download_post(posts, username, loader)


def main(user_input, user='', password=''):
    loader = instaloader.Instaloader()

    # Login using the credentials
    if user and password:
        loader.login(user, password)

    user_id = None
    if "https" in user_input:
        identify_link = user_input.split('/')
        if identify_link == 'p':
            short_code = user_input.split('/')[4]
            post = instaloader.Post.from_shortcode(loader.context, short_code)
            username = post.owner_username
            loader.download_post(post, target=username)
            organise_file(username)
        else:
            user_id = user_input.split('/')[3].split('?')[0]
    else:
        user_id = user_input

    if user_id:
        # Use Profile class to access metadata of account
        profile = instaloader.Profile.from_username(loader.context, user_id)
        private = profile.is_private
        if profile and not private:
            # date_from = '2023'
            download(profile, loader)
        else:
            print("profile is private or username incorrect")


if __name__ == "__main__":
    main("")
