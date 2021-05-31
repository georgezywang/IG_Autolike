# IG_Autolike
Instagram auto like bot for personal use, implemented using [Instapy](https://github.com/timgrossmann/InstaPy) and [instaloader](https://github.com/instaloader/instaloader).

## Dependencies
Dependencies listed in `requirements.txt`. Install using `pip3 install -r requirements.txt`. A Firefox browser also needs to be installed on the machine.

## Autolike
To auto like `n` posts, run `python3 IG_Autolike.py -u your_username -p your_password -a n`. The program will only like posts posted by people who you follow and follows you, unless otherwise specified in the `whiteList` parameter in `Config.yaml`. There are additional hyperparameter one can specify in `Config.yaml`, the variable names should be self explanatory.

## Following Management
The script also provides functionalities to unfollow nonfollowers followed by the user. Exceptions can be made by adding whitelist usernames to the `unfollowWhiteList` array in `Config.yaml`. To use the following management functionality, run `python3 IG_Autolike.py -u your_username -p your_password -f`.

## Updates
### May 31, 2021 Update
The function `session.like_by_feed` is experiencing errors since Instagram has updated their webpage structures, that for any instagram post's window object, `window.__additionalData` is now empty. This [InstaPy Issue](https://github.com/timgrossmann/InstaPy/issues/6191) has extensive discussion regarding this problem. Currently, there is a temporary [bug fix](https://github.com/timgrossmann/InstaPy/pull/6195) that has not been merged into `main`. It works fine for me. To install the fix, run `pip3 install -I https://github.com/schealex/InstaPy/zipball/develop`