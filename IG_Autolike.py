import argparse
import yaml
import instaloader
import threading
import signal
import sys

from instapy import InstaPy
from instapy.util import web_address_navigator, get_relationship_counts
from instapy.like_util import get_links_from_feed, check_link, like_image, verify_liking
from selenium.common.exceptions import NoSuchElementException
from colorama import Style, Fore
from typing import List, Set

def Ig_Auto_Like(
    maxLikes : int = 2000, 
    minLikes : int = 10, 
    maxFollowers : int = 10000, 
    minFollowing : int = 30, 
    minFollowers : int = 30, 
    whiteList : List[str] = [], 
    unfollowWhiteList : List[str] = []
):

    # similar implementation as InstaPy.like_by_feed_generator()
    # autolike instagram posts and manage followees if specified

    session.login()

    postsLiked : int = 0
    numOfSearch : int = 0
    linkNotFoundLoopError : int = 0
    history : List[str] = []
    alreadyLiked : int = 0
    whiteListLike : int = 0
    postByNonFollowees : int = 0
    breakOuterLoop : bool = False

    unfollowWhiteList = set(unfollowWhiteList)

    while (postsLiked < NUM_POSTS):

        if (breakOuterLoop):
            break

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
                breakOuterLoop = True
                break

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
                except KeyError as e:
                    print(Fore.RED + "KEYERROR EXCEPTION: {}".format(e))
                    print(
                         "This is likely due to the current InstaPy library implementation. Try run `pip3 install -I https://github.com/schealex/InstaPy/zipball/develop` to install the fix. If you believe this is not the cause, comment out this exception handler." + Style.RESET_ALL
                    )
                    print("For more information, refer to https://github.com/timgrossmann/InstaPy/issues/6191 and https://github.com/timgrossmann/InstaPy/pull/6195")
                    breakOuterLoop = True
                    break
                except Exception as ex:
                    session.logger.info("EXCEPTION ENCOUNTERED: {}, continuing...".format(ex))
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
                
                if userName not in SELF_FOLLOWEES:
                    postByNonFollowees += 1
                    session.logger.warning("{} is not a followee, skipping...".format(userName))

                    if postByNonFollowees > NUM_POSTS / 8:
                        session.logger.info("{} posts by non followees in feed, aborting".format(postByNonFollowees))
                        breakOuterLoop = True
                        break

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
                        breakOuterLoop = True
                        break

    session.logger.info("Finished Liking {} / {} Posts".format(postsLiked, NUM_POSTS))

    if (ARGS.unfollow):
        if (not CONTACTS_RETRIEVED):
            print(Fore.RED + "THREADINFO | Auto Like Thread (UNFOLLOW) Waiting For Secure Contacts Set" + Style.RESET_ALL)
            CONTACTS_EVENT.wait()
            print(Fore.GREEN + "THREADINFO | Auto Like Thread (UNFOLLOW) Resuming" + Style.RESET_ALL)
        Manage_Contacts(unfollowWhiteList)

def Get_Secure_Contacts():
    # get list of users that are both follower and followee

    global SECURE_CONTACTS
    global CONTACTS_RETRIEVED
    global SELF_FOLLOWERS
    global SELF_FOLLOWEES

    print(Fore.GREEN + "THREADINFO | Getting Secure Contacts" + Style.RESET_ALL)

    loader = instaloader.Instaloader()
    loader.login(USERNAME, PASSWORD)
    profile = instaloader.Profile.from_username(loader.context, USERNAME)
    followees = profile.get_followees()
    followers = profile.get_followers()

    SELF_FOLLOWERS = {f.username for f in followers}
    SELF_FOLLOWEES = {f.username for f in followees}
    SECURE_CONTACTS = SELF_FOLLOWEES.intersection(SELF_FOLLOWERS)

    CONTACTS_RETRIEVED = True
    CONTACTS_EVENT.set()

    print(Fore.GREEN + "THREADINFO | Thread Finished Processing Secure Contacts" + Style.RESET_ALL)

def Manage_Contacts(unfollowWhiteList : Set[str]):
    # unfollow nonfollowers followed by the user

    toUnfollow : List[str] = []
    nonfollower = SELF_FOLLOWEES.difference(SELF_FOLLOWERS)
    
    for userName in nonfollower:
        if userName not in unfollowWhiteList:
            usrFollowerCnt, usrFollowingCnt = get_relationship_counts(
                            session.browser, userName, session.logger
                        )
            if usrFollowerCnt < cfg["maxFollowers"]:
                toUnfollow.append(userName)
                session.logger.info("{} will be unfollowed".format(userName))
        else:
            session.logger.info("User {} in unfollow white list, skipping".format(userName))

    session.unfollow_users(
        amount = len(toUnfollow),
        custom_list_enabled = True,
        custom_list = toUnfollow,
        custom_list_param = "all",
        style = "RANDOM",
        unfollow_after = None,
        sleep_delay = 60
    )

def Browser_Signal_Handler(sig, frame):
    # Signal handler for keyboard interruption

    session.logger.info("Process Terminated through SIGINT")
    sys.exit(0)

def Main():
    # Main thread

    contactThread = threading.Thread(target = Get_Secure_Contacts)
    autoLikeThread = threading.Thread(target = Ig_Auto_Like, kwargs = cfg)
    contactThread.daemon = True
    
    contactThread.start()
    autoLikeThread.start()
    contactThread.join()
    autoLikeThread.join()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, Browser_Signal_Handler)
    
    ARG_PARSER = argparse.ArgumentParser()
    ARG_PARSER.add_argument("-u", "--username", help = "your ig username", required = True)
    ARG_PARSER.add_argument("-p", "--password", help = "your ig password", required = True)
    ARG_PARSER.add_argument("-a", "--amount", type = int, help = "posts to like", required = False, default = 0)
    ARG_PARSER.add_argument("-f", "--unfollow", help = "whether to unfollow nonfollowers", action='store_true')

    ARGS = ARG_PARSER.parse_args()
    USERNAME = ARGS.username
    PASSWORD = ARGS.password
    NUM_POSTS = ARGS.amount

    with open('Config.yaml', 'r') as cfgFile:
        cfg = yaml.load(cfgFile, yaml.SafeLoader)

    CONTACTS_RETRIEVED = False
    CONTACTS_EVENT = threading.Event()

    SECURE_CONTACTS : Set[str] = set()
    SELF_FOLLOWERS : Set[str] = set()
    SELF_FOLLOWEES : Set[str] = set()

    session = InstaPy(username= USERNAME, password= PASSWORD)
    Main()
    session.browser.close()