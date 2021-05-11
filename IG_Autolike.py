import argparse
import yaml
import instaloader
import threading

from instapy import InstaPy
from instapy.util import web_address_navigator, get_relationship_counts
from instapy.like_util import get_links_from_feed, check_link, like_image, verify_liking
from selenium.common.exceptions import NoSuchElementException
from colorama import Style, Fore

def Ig_Auto_Like(maxLikes=2000, minLikes=10, maxFollowers=10000, minFollowing=30, minFollowers=30, whiteList = []):
    session = InstaPy(username= USERNAME, password= PASSWORD)
    session.login()

    # similar implementation as InstaPy.like_by_feed_generator()

    postsLiked = 0
    numOfSearch = 0
    linkNotFoundLoopError = 0
    history = []
    alreadyLiked = 0
    whiteListLike = 0

    while (postsLiked < NUM_POSTS):
        try:
            links = get_links_from_feed(
                session.browser, NUM_POSTS, numOfSearch, session.logger
            )

            if len(links) > 0:
                linkNotFoundLoopError = 0

            if len(links) == 0:
                linkNotFoundLoopError += 1
                if linkNotFoundLoopError >= 10:
                    session.logger.warning(
                        "Loop error, 0 links"
                        " for 10 times consecutively, exit loop"
                    )
                    break

        except NoSuchElementException:
            session.logger.warning("Too few images, aborting")
            session.aborting = True
            return

        numOfSearch += 1

        for _, link in enumerate(links):
            if postsLiked == NUM_POSTS:
                return

            if link in history:
                session.logger.info(
                    "This link has already been visited: {}".format(
                        link)
                )
                continue
            else:
                session.logger.info("New link found...")
                history.append(link)
                session.logger.info(
                    "[{} posts liked / {} amount]".format(
                        postsLiked, NUM_POSTS)
                )
                session.logger.info(link)

                try:
                    (
                        inappropriate,
                        userName,
                        isVideo,
                        reason,
                        scope,
                    ) = check_link(
                        session.browser,
                        link,
                        session.dont_like,
                        session.mandatory_words,
                        session.mandatory_language,
                        session.is_mandatory_character,
                        session.mandatory_character,
                        session.check_character_set,
                        session.ignore_if_contains,
                        session.logger,
                    )
                except:
                    continue
                
                if whiteListLike < NUM_POSTS / 3 and userName in whiteList:
                    session.logger.info("{} is in the whitelist".format(userName))
                    likeState, msg = like_image(
                        session.browser,
                        userName,
                        session.blacklist,
                        session.logger,
                        session.logfolder,
                        postsLiked,
                    )

                    if likeState is True:
                        postsLiked += 1
                        whiteListLike += 1
                        session.jumps["consequent"]["likes"] = 0
                    else:
                        alreadyLiked += 1
                    
                    continue
                
                if (not CONTACTS_RETRIEVED):
                    print(Fore.RED + "THREADINFO | Auto Like Thread Waiting For Secure Contacts Set" + Style.RESET_ALL)
                    CONTACTS_EVENT.wait()
                    print(Fore.GREEN + "THREADINFO | Auto Like Thread Resuming" + Style.RESET_ALL)

                if userName not in SECURE_CONTACTS:
                    session.logger.info("User Name not in secure contacts, skipping...")
                    continue
                
                if isVideo or inappropriate:
                    session.logger.info("Post is video or inappropriate, skipping...")
                    continue
                
                session.liking_approved = verify_liking(
                    session.browser,
                    maxLikes,
                    minLikes,
                    session.logger,
                )

                usrFollowerCnt, usrFollowingCnt = get_relationship_counts(
                    session.browser, userName, session.logger
                )

                if (usrFollowerCnt > maxFollowers or usrFollowerCnt < minFollowers or usrFollowingCnt < minFollowing):
                    session.logger.info("User follower / following count out of range, skipping...")
                    continue

                minLikes = max(minLikes, usrFollowerCnt / 30)

                if session.liking_approved:
                        # validate user
                    validation, details = session.validate_user_call(userName)
                    if validation is not True:
                        session.logger.info(details)
                        not_valid_users += 1
                        continue
                    else:
                        web_address_navigator(session.browser, link)

                    # try to like
                    likeState, msg = like_image(
                        session.browser,
                        userName,
                        session.blacklist,
                        session.logger,
                        session.logfolder,
                        postsLiked,
                    )

                    if likeState is True:
                        postsLiked += 1
                        session.jumps["consequent"]["likes"] = 0
                    else:
                        alreadyLiked += 1
                    
                    if alreadyLiked >= NUM_POSTS / 3:
                        session.logger.info("Too much already liked posts, terminating")
                        session.logger.info("Already liked {} / Amount {}".format(alreadyLiked, NUM_POSTS))
                        return

    session.logger.info("Finished Liking {} Posts".format(postsLiked)) 

def Get_Secure_Contacts():
    global SECURE_CONTACTS
    global CONTACTS_RETRIEVED

    print(Fore.GREEN + "THREADINFO | Getting Secure Contacts" + Style.RESET_ALL)
    loader = instaloader.Instaloader()
    loader.login(USERNAME, PASSWORD)
    profile = instaloader.Profile.from_username(loader.context, USERNAME)
    followees = profile.get_followees()
    followers = profile.get_followers()

    selfFollowers = set()
    selfFollowees = set()
    for f in followees:
        selfFollowees.add(f.username)
    for f in followers:
        selfFollowers.add(f.username)

    SECURE_CONTACTS = selfFollowees.intersection(selfFollowers)
    CONTACTS_RETRIEVED = True
    CONTACTS_EVENT.set()

    print(Fore.GREEN + "THREADINFO | Thread Finished Processing Secure Contacts" + Style.RESET_ALL)

def Main():
    with open('Config.yaml', 'r') as cfgFile:
        cfg = yaml.load(cfgFile, yaml.SafeLoader)

    contactThread = threading.Thread(target = Get_Secure_Contacts)
    autoLikeThread = threading.Thread(target = Ig_Auto_Like, kwargs = cfg)
    contactThread.start()
    autoLikeThread.start()
    contactThread.join()
    autoLikeThread.join()


if __name__ == "__main__":
    ARG_PARSER = argparse.ArgumentParser()
    ARG_PARSER.add_argument("-u", "--username", help = "your ig username", required = True)
    ARG_PARSER.add_argument("-p", "--password", help = "your ig password", required = True)
    ARG_PARSER.add_argument("-a", "--amount", type = int, help = "posts to like", required = True)

    ARGS = ARG_PARSER.parse_args()
    USERNAME = ARGS.username
    PASSWORD = ARGS.password
    NUM_POSTS = ARGS.amount

    CONTACTS_RETRIEVED = False
    CONTACTS_EVENT = threading.Event()
    SECURE_CONTACTS = set()

    Main()
