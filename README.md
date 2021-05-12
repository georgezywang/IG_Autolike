# IG_Autolike
Instagram auto like bot for personal use, implemented using [Instapy](https://github.com/timgrossmann/InstaPy) and [instaloader](https://github.com/instaloader/instaloader).

## Dependencies
Dependencies listed in `requirements.txt`. Install using `pip3 install -r requirements.txt`. A Firefox browser also needs to be installed on the machine.

## Autolike
To auto like `n` posts, run `python3 IG_Autolike.py -u your_username -p your_password -a n`. The program will only like posts posted by people who you follow and follows you, unless otherwise specified in the `whiteList` parameter in `Config.yaml`. There are additional hyperparameter one can specify in `Config.yaml`, the variable names should be self explanatory.

## Following Management
The script also provides functionalities to unfollow nonfollowers followed by the user. Exceptions can be made by adding whitelist usernames to the `unfollowWhiteList` array in `Config.yaml`. To use the following management functionality, run `python3 IG_Autolike.py -u your_username -p your_password -f`.

