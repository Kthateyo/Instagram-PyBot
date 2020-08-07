from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time, random, datetime
import statistics, config
from path import Path


###############################
# CLASSES

class ActionBlock(Exception):
    pass


###############################
# FUNCTIONS

def get_credentials():
    username = ""
    password = ""

    if not Path(config.data.credential_file).exists():
        print("[ERROR]: File with credentials is not exist")
        exit()

    with open(Path(config.data.credential_file), 'r', encoding="utf-8") as f:
        lines = f.readlines()
        username = lines[0].strip()
        password = lines[1].strip()

    if username == "" and password == "":
        print("[ERROR]: File with credentials is empty. First line expected login. Second line expected password.")
        exit()

    return (username, password)


def get_comments():
    comments = []
    with open(Path(config.data.comments_file), 'r', encoding="utf-8") as f:
        comments = [line.strip() for line in f.readlines()]
    return comments


def get_emojis():
    emojis = []
    with open(Path(config.data.emojis_file), 'r', encoding="utf-8") as f:
        emojis = [line.strip() for line in f.readlines()]
    return emojis


def check_restrictness():
    try:
        driver.find_element_by_css_selector("div[role=dialog]")
        ok_button = driver.find_element_by_css_selector("button.HoLwm")
        time.sleep(random.uniform(1,3))
        ok_button.click()

        statistics.update(statistics.Data.ERRORS, message="Instagram ActionBlock error")
        
        raise ActionBlock
    except NoSuchElementException:
        pass


def type_in(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))


def sleep(seconds, interval=10):
    now = str(datetime.datetime.now().strftime("%H:%M:%S"))
    to = str((datetime.datetime.now() + datetime.timedelta(seconds=seconds)).strftime("%H:%M:%S"))
    print(f"[SLEEP]: Now is {now} Waiting to {to}. Checking frequency: {seconds} seconds.")

    while seconds > 0:
        time.sleep(interval)
        seconds -= interval


def remove_duplicates(arr):
    result = []
    for item in arr:
        if item not in result:
            result.append(item)

    return result


def driver_init():
    
    if config.data.web_browser_driver == "" or not Path(config.data.web_browser_driver).exists():
        print("[ERROR]: Path to chrome webdriver not found. Check your config.json file.")

    global driver
    if config.data.headless:
        options = webdriver.chrome.options.Options()
        options.headless = True
        driver = webdriver.Chrome(Path(config.data.web_browser_driver), options=options)
    else:
        driver = webdriver.Chrome(Path(config.data.web_browser_driver))

    driver.implicitly_wait(1)


def driver_close():
    driver.quit()


def log_in():
    driver.get("https://instagram.com")
    
    password_field = None
    try:
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
    except:
        driver.quit()
    
    username_field = driver.find_element_by_name("username")
    
    credentials = get_credentials()
    type_in(username_field, credentials[0])
    type_in(password_field, credentials[1])
    del credentials

    password_field.send_keys(Keys.RETURN)
    time.sleep(random.uniform(4,6))
    
    driver.get("https://instagram.com")

    try:
        not_now_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role=dialog] button.HoLwm"))
            )
        not_now_button.click()
    except:
        pass
    
    time.sleep(random.uniform(2,4))
    get_following_count()


def get_following_count():
    change_site_profile()
    following_div = driver.find_element_by_css_selector('a[href*="following"]')
    global followings
    followings = int(following_div.find_element_by_css_selector("span.g47SY").text)


def log_out():
    profile_div = driver.find_element_by_css_selector("div.Fifk5 > span[role=link]")
    profile_div.click()
    time.sleep(random.uniform(0.5,2))
    log_out_div = driver.find_element_by_css_selector("div._01UL2 > div[role=button]")
    log_out_div.click()

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
    except:
        pass


def change_site_hashtag(name):
    while name[0] == '#':
        name = name[1:]
    driver.get(f"https://www.instagram.com/explore/tags/{name}/")


def change_site_person(name):
    driver.get(f"https://www.instagram.com/{name}/")


def change_site_main():
    driver.get("https://www.instagram.com")


def change_site_profile():
    profile_div = driver.find_element_by_css_selector("div.Fifk5 > span[role=link]")
    profile_div.click()
    time.sleep(random.uniform(0.5,2))
    profile_button = driver.find_element_by_css_selector("div._01UL2 > a.-qQT3")
    profile_button.click()
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "be6sR")))
        return True
    except NoSuchElementException:
        return False
    return False


def change_site(name=""):
    if name[0] == '#':
        change_site_hashtag(name)
    elif name == "":
        change_site_main()
    elif name == "profile":
        change_site_profile()
    else:
        change_site_person(name)


def like(post):
    is_liked = bool(post.find_elements_by_css_selector('span.fr66n button.wpO6b svg[fill="#ed4956"]'))
    
    if not is_liked:
        try:
            like_button = post.find_element_by_css_selector("span.fr66n button.wpO6b")
            like_button.click()

            check_restrictness()

            statistics.update(statistics.Data.LIKES)
            return True
        except NoSuchElementException:
            return False
    return False


def comment(post):
    try:
        textarea = post.find_element_by_class_name("Ypffh")
    
        text = random.choice(get_comments()) + " "
        for _ in range(random.randint(0,3)):
            text += random.choice(get_emojis())

        text = text.strip()

        textarea.click()
        textarea = post.find_element_by_class_name("Ypffh")
        type_in(textarea, text)
        textarea.send_keys(Keys.RETURN)

        error = bool(driver.find_elements_by_class_name("HGN2m"))
        if error:
            statistics.update(statistics.Data.ERRORS, message="Couldn't post comment")
            return False

        check_restrictness()

        statistics.update(statistics.Data.COMMENTS)
        return True
    except NoSuchElementException:
        return False


def follow(post):
    is_followed = bool(post.find_elements_by_css_selector("div.bY2yH button._8A5w5"))

    if not is_followed:
        try:
            follow_button = driver.find_element_by_css_selector("div.bY2yH button.y3zKF")
            follow_button.click()

            check_restrictness()

            statistics.update(statistics.Data.FOLLOWS)
            global followings
            followings += 1
            return True
        except NoSuchElementException:
            return False
    return False


def unfollow(post):
    is_followed = bool(post.find_elements_by_css_selector("div.bY2yH button._8A5w5"))

    if is_followed:
        try:
            follow_button = driver.find_element_by_css_selector("div.bY2yH button._8A5w5")
            follow_button.click()
            red_unfollow_button = driver.find_element_by_class_name("-Cab_")
            red_unfollow_button.click()

            check_restrictness()

            statistics.update(statistics.Data.UNFOLLOWS)
            global followings
            followings -= 1
            return True
        except NoSuchElementException:
            return False
    return False


def unfollow_in_profile():
    global followings
    get_following_count()

    unfollow_limit = not (config.data.chance_of_unfollow > 0 
        and statistics.get(statistics.Data.UNFOLLOWS, hours=1) < config.data.max_unfollows_per_hour 
        and statistics.get(statistics.Data.UNFOLLOWS, hours=24) < config.data.max_unfollows_per_day
        and followings > config.data.min_of_followings)

    if unfollow_limit:
        return
    
    change_site_profile()
    following_div = driver.find_element_by_css_selector('a[href*="following"]')

    time.sleep(random.uniform(1,2))
    following_div.click()
    time.sleep(random.uniform(1,2))
    following_list_div = driver.find_element_by_class_name("PZuss")

    # Scroll down
    count = 0
    following_list = following_list_div.find_elements_by_tag_name("li")
    while count != followings:
        driver.execute_script(f'document.getElementsByClassName("PZuss")[0].lastChild.scrollIntoView()')
        time.sleep(random.uniform(1,2))
        following_list = following_list_div.find_elements_by_tag_name("li")
        count = len(following_list)
    
    while not unfollow_limit:
        following = following_list.pop(random.randint(0, len(following_list)-1))
        
        unfollow_button = following.find_element_by_tag_name("button")
        unfollow_button.click()
        time.sleep(random.uniform(1,2))

        red_unfollow_button = driver.find_element_by_class_name("-Cab_")
        red_unfollow_button.click()
        check_restrictness()
        
        statistics.update(statistics.Data.UNFOLLOWS)
        followings -= 1
        config.handle_args()
        unfollow_limit = not (config.data.chance_of_unfollow > 0 
            and statistics.get(statistics.Data.UNFOLLOWS, hours=1) < config.data.max_unfollows_per_hour 
            and statistics.get(statistics.Data.UNFOLLOWS, hours=24) < config.data.max_unfollows_per_day
            and followings > config.data.min_of_followings)
        time.sleep(random.uniform(1,2))
    

def work_on_site():
    error = False
    gonna_change_site = False
    is_limit_reached = False

    post_nr = 0
    posts = []
    # While ERROR or ChangeSite or LimitReached
    while (not error) and (not gonna_change_site) and (not is_limit_reached):
        config.handle_args()

        if config.data.verbose:
            print("Last 24H:", "LIKES:", statistics.get(statistics.Data.LIKES, hours=24), "COMMENTS:", statistics.get(statistics.Data.COMMENTS, hours=24), "FOLLOWS:", statistics.get(statistics.Data.FOLLOWS, hours=24), "UNFOLLOWS:", statistics.get(statistics.Data.UNFOLLOWS, hours=24))
            print("Last 1H:", "LIKES:", statistics.get(statistics.Data.LIKES), "COMMENTS:", statistics.get(statistics.Data.COMMENTS), "FOLLOWS:", statistics.get(statistics.Data.FOLLOWS), "UNFOLLOWS:", statistics.get(statistics.Data.UNFOLLOWS))

        posts += driver.find_elements_by_class_name("v1Nh3")
        posts = remove_duplicates(posts)
        post = posts[post_nr]

        # For each post
        post.click()
        time.sleep(random.uniform(0.5,2))

        # If post not loaded
        try: 
            post_dialog = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "M9sTE")))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "fr66n")))
        except:
            driver.find_element_by_tag_name("body").send_keys(Keys.ESCAPE)
            post_nr += 1
            time.sleep(random.uniform(0.5,2))
            continue

        like_limit = ((config.data.max_likes_per_hour != -1 and statistics.get(statistics.Data.LIKES, hours=1) >= config.data.max_likes_per_hour)
                  or (config.data.max_likes_per_day != -1 and statistics.get(statistics.Data.LIKES, hours=24) >= config.data.max_likes_per_day))
        comment_limit = ((config.data.max_comments_per_hour != -1 and statistics.get(statistics.Data.COMMENTS, hours=1) >= config.data.max_comments_per_hour)
                     or (config.data.max_comments_per_day != -1 and statistics.get(statistics.Data.COMMENTS, hours=24) >= config.data.max_comments_per_day))
        follow_limit = ((config.data.max_follows_per_hour != -1 and statistics.get(statistics.Data.FOLLOWS, hours=1) >= config.data.max_follows_per_hour)
                    or (config.data.max_follows_per_day != -1 and statistics.get(statistics.Data.FOLLOWS, hours=24) >= config.data.max_follows_per_day)
                    or followings >= config.data.max_of_followings)
        unfollow_limit = ((config.data.max_unfollows_per_hour != -1 and statistics.get(statistics.Data.UNFOLLOWS, hours=1) >= config.data.max_unfollows_per_hour)
                      or (config.data.max_unfollows_per_hour != -1 and statistics.get(statistics.Data.UNFOLLOWS, hours=24) >= config.data.max_unfollows_per_hour))
        
        # like
        if not like_limit and random.random() < config.data.chance_of_like:
            like(post_dialog)
            time.sleep(random.uniform(0.5,2))

        # if liked:
            # comment
            if not comment_limit and random.random() < config.data.chance_of_comment:
                comment(post_dialog)
                time.sleep(random.uniform(1,3))

            # follow
            if not follow_limit and random.random() < config.data.chance_of_follow:
                follow(post_dialog)
                time.sleep(random.uniform(0.5,2))

        else:
            # unfollow
            if not unfollow_limit and random.random() < config.data.chance_of_unfollow:
                unfollow(post_dialog)
                time.sleep(random.uniform(0.5,2))
        
        # Back to site
        driver.find_element_by_tag_name("body").send_keys(Keys.ESCAPE)
        post_nr += 1

        if post_nr > 10 and random.random() < config.data.chance_of_change_site:
            gonna_change_site = True
        
        if like_limit:
            is_limit_reached = True
            return is_limit_reached
        

        time.sleep(random.uniform(0.5,2))
    return False


def work_on():
    site = False
    main = False

    try:
        site = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.CLASS_NAME, "v1Nh3"))
            )
        site = bool(site)
    except:
        pass

    try:
        main = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.CLASS_NAME, "M9sTE"))
            )
        main = bool(main)
    except:
        pass

    if site:
        work_on_site()
    # elif main:
    #     like_on_main()
    # else:
    #     print("[ERROR]", "It's not site neither main")

