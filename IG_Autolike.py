import argparse
import yaml

from instapy import InstaPy
from instapy.util import smart_run

def Main(MAX_LIKES = 2000, MIN_LIKES = 10, MAX_FOLLOWERS = 10000, MIN_FOLLOWING = 30, MIN_FOLLOWERS = 30):
    session = InstaPy(username= USERNAME, password= PASSWORD)
    session.login()
    account_followers = set(session.grab_followers(username=USERNAME, amount="full"))
    account_following = set(session.grab_following(username=USERNAME, amount="full"))
    unsecure_contacts = list(account_followers.union(account_following).difference(account_followers.intersection(account_following)))

    session.set_ignore_users(unsecure_contacts) # unsecure_contacts
    session.set_delimit_liking(enabled=True, max_likes=MAX_LIKES, min_likes=MIN_LIKES)
    session.set_relationship_bounds(enabled=True,
                                    potency_ratio=None,
                                    delimit_by_numbers=True,
                                    max_followers=MAX_FOLLOWERS,
                                    max_following=None,
                                    min_followers=MIN_FOLLOWERS,
                                    min_following=MIN_FOLLOWING,
                                    min_posts=None,
                                    max_posts=None)

    session.like_by_feed(amount=30, randomize=False, unfollow=False, interact=False)

if __name__ == "__main__":
    ARG_PARSER = argparse.ArgumentParser()
    ARG_PARSER.add_argument("-u", "--username", help = "your ig username", required = True)
    ARG_PARSER.add_argument("-p", "--password", help = "your ig password", required = True)
    ARGS = ARG_PARSER.parse_args()
    USERNAME = ARGS.username
    PASSWORD = ARGS.password

    with open('Config.yaml', 'r') as cfgFile:
        cfg = yaml.load(cfgFile)
    
    Main(**cfg)