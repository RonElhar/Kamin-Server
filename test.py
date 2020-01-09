from Controllers.discussion_controller import DiscussionController
from Controllers.user_controller import UserController
from Entities.comment import *
from datetime import datetime
import TreeTools.TreeTools as tt


def create_discussion_on_db(discussion_id=0, discussion_path='D:\\Kamin-Server\\resources\\discussions\\80919_labeled_trees.txt'):
    trees = tt.load_list_of_trees(discussion_path)
    root_tree = trees[discussion_id]
    dc = DiscussionController()
    disc_id = dc.create_discussion(root_tree['node']['extra_data']['title'], ["Life", "Pregnant", "Abortion"], None)
    root_comment = CommentNode(author=root_tree['node']['author'], text=root_tree['node']['text'], parent_id=None,
                               discussion_id=disc_id, extra_data=root_tree['node']['extra_data'],
                               labels=root_tree['node']['labels'] if 'labels' in root_tree['node'] else None,
                               depth=0, time_stamp=datetime.fromtimestamp(root_tree['node']['timestamp']),
                               child_comments=[])
    response = dc.add_comment(root_comment)
    comment_id = response["comment_id"]
    root_comment.set_id(comment_id)
    [traverse_add_comments(child, root_comment.get_id(), 1, disc_id, dc) for child in root_tree['children']]


def traverse_add_comments(comment_tree, parent_id, depth, disc_id, dc):
    comment_node = CommentNode(author=comment_tree['node']['author'], text=comment_tree['node']['text'],
                               parent_id=parent_id, discussion_id=disc_id, extra_data=comment_tree['node']['extra_data'],
                               labels=comment_tree['node']['labels'] if 'labels' in comment_tree['node'] else None,
                               depth=depth, time_stamp=datetime.fromtimestamp(comment_tree['node']['timestamp']),
                               child_comments=[])
    response = dc.add_comment(comment_node)
    comment_id = response["comment_id"]
    comment_node.set_id(comment_id)
    [traverse_add_comments(child, comment_node.get_id(), depth + 1, disc_id, dc) for child in
     comment_tree['children']]


def get_discussion_from_db():
    dc = DiscussionController()
    id = "5e0795acccadf5b7189464dd"
    return dc.get_discussion(id)


def add_new_user():
    user_controller = UserController()
    return user_controller.add_new_user("gal21", "1234", "gal", "Esco")


def get_user():
    user_controller = UserController()
    return user_controller.get_user("gal21")


# create_discussion_on_db()
discussion = get_discussion_from_db()
json_dict = discussion.to_json_dict()
# user_id = add_new_user()
# user = get_user()
# val = user.verify_password("1234")
print("bla")















# dc = DiscussionController()
# disc_id = dc.create_discussion("good people", ["life", "fun", "bla"], None)
# print(type(disc_id))
# print("bla")
#
# comment_node = CommentNode(author="Slagernicus", text="Abortion should be legal in my opinion for 4 main reasons (I understand there are more, I am just offering up 4 of my own). 1: Pregnancy\u2019s affect on the female\u2019s life 2: Relationship between fetus and host 3: Pregnancy circumstances 4. Overpopulation (yes, I went there) Pregnancy\u2019s Effects on the Female\u2019s Life: When you are pregnant, if you would like your baby to be healthy, there are plenty of things you should/shouldn\u2019t do, which can drastically alter your lifestyle. You may have to quit a lot of your favorite hobbies. You may not be able to work your job anymore. You\u2019ll be physically restricted in a lot of ways. This process lasts around 38 weeks. You also gain weight, which takes a while to lose after the baby is born and can cause a lot of self-consciousness issues in females directly following child birth. You will most likely have lower back pain/soreness or problems with posture once your belly begins to increase in size. Your day to day life will not be as physically involved as usual, which can affect your career and health, depending on what activities you were accustomed to performing before you got pregnant. In the gym, you are no longer supposed to live heavy weights, or perform high-impact exercises. This can be a problem if you are an avid gym goer. You can\u2019t scuba dive, water skii, do contact sports, and it\u2019s recommended to not eat too many seafood options due to high mercury content. Some people live as if they were going to die the next day. Those people tend to live lives full of extreme sports, fun, and danger. If you are one of those people, would you not want to be able to remove the limiting factor from your life by getting an abortion? Relationship Between Fetus and Host: In scientific terms, a parasitic relationship is classified as a relationship in which one organism, the parasite, lives in or on another organism, the host, and is harmful to it. Well, a fetus is harmful in the sense that it detracts nutrients from the daily food you eat, similar to a tapeworm. Additionally, pregnancy can cause fatigue, nausea, tender/swollen breasts, heartburn, constipation, increased stress levels, mood swings, bouts of sadness, decreased sex life, increased risk of iron deficiency anemia, increased stress on the heart, hearth rhythm issues, heart valve issues, congestive heart failure, worsening of asthma, increased risk of developing blood clots in legs if you have atrial fibrillation, back pain, severe depression (if a miscarriage occurs), anxiety, shortness of breath, leg cramps, decreased sleep, breast growth, contractions (duh), spider veins, frequent urination, vaginal discharge, food aversion/cravings, and in worst case, death. Yes, death due to pregnancy is still a real thing. \"over 600 women die each year in the United States as a result of pregnancy or delivery complications\" - the CDC (yeah yeah I know it's not really a CDC quote but i'm lazy and it was on the CDC website) Clearly, a fetus does not have a healthy impact on the body. Some pregnancy\u2019s go off without a hitch, and are relatively pleasant in comparison to others, but the pregnancy process generally affects the body in a couple severe ways. Pregnancy Circumstances: A woman can get pregnant in many different ways. If a woman is raped, and becomes pregnant, should she be forced to keep the child? If a woman has a one night stand while using birth control, and becomes pregnant, should she be forced to keep the child? If a woman has a one night stand and the condom breaks, resulting in her pregnancy, should she be forced to keep the child? If a woman lives on her own, with absolutely no living relatives, family members, and a deceased partner, who impregnated her before his death, and her career is a career that will be lost, or severely hampered by pregnancy, should she be forced to keep the child? If a woman does not have the financial means of supporting a child, and becomes pregnant, should she be forced to keep the child? If a lesbian couple decide to have a baby, and one of the females becomes pregnant through insemination, and then they break up, or they both decide they don\u2019t want the baby, should a baby be forced upon them? If a woman is pregnant, and is scared of the outcome of the pregnancy, or scared of death (although rare, it still happens), should she be forced to endure childbirth? If a woman is pregnant, and no longer wants the baby/regrets her decision to get pregnant, should she be forced to suffer the pains of childbirth, and the side effects of pregnancy? My answer is no to all of these. Your opinion may differ, but I believe it to be a woman\u2019s right (and if a man could somehow get pregnant, a man\u2019s right) to have control over her own body. If I had a tapeworm inside of me, I would want it removed. If I somehow ended up having a baby puppy inside of me, that was going to take 38 weeks to come out of me, and could potentially kill me or hurt me, I would weigh my options, look up statistics, and depending on the risk factor make a decision based on the outlook of my future and my current desires. Perhaps I would keep the puppy and life would be great, or perhaps I would not keep the puppy due to the impact it would have on my life. Either way, I would want the freedom of choice. Overpopulation: The title of this section explains itself. There are way too many people on the planet right now. Earth\u2019s resources are limited, we should not be growing the population anymore, in fact we should probably try to slowly decrease the population to a stable and more manageable number. There is no need to explain anything here about overpopulation, this is about abortion. Overpopulation is a huge problem for the environment and our planet, and abortion is one way of reducing population growth. That is why this is one of the 4 main reasons I believe abortion should be allowed. http://www.broitsablog.com/?p=181",
#                                   parent_id=None, discussion_id=disc_id,
#                                   extra_data={"file:line": "4rl42j_00_02:0",
#                                               "subreddit": "changemyview",
#                                               "from_kind": None,
#                                               "from": None,
#                                               "title": "CMV: Abortion should remain legal",
#                                               "num_comments": 129,
#                                               "subreddit_id": "t5_2w2s8",
#                                               "downs": 0, "saved": False,
#                                               "from_id": None,
#                                               "permalink": "/r/changemyview/comments/4rl42j/cmv_abortion_should_remain_legal/",
#                                               "name": "t3_4rl42j",
#                                               "url": "https://www.reddit.com/r/changemyview/comments/4rl42j/cmv_abortion_should_remain_legal/",
#                                               "ups": 17}, actions=[], labels={},
#                            depth=1, time_stamp=1467843645, child_comments=[])
#
# response = dc.add_comment(comment_node)
# print("bla")

#b'^\x07\x83\xdebw\x08\x18\x17\xf4s\x8f'
# id = ObjectId('5e0787f0b6758c5c0464e606')
# id2 = ObjectId(b'XgeD3WJ3CBgX9HOO')
# print("bla")
# 5e0783dd6277081817f4738e
# XgeD3WJ3CBgX9HOO

# 5e077362aa3027839b9278a6
# Binary('XgdzYqowJ4Obknim', 0)

# id = .encode()
# bytes1 = bytes("5e077362aa3027839b9278a6", 'utf-8')
# print(id)




#
# comment_node2 = CommentNode(author="Hq3473", text="Up until which point should abortion be legal? Should a woman be able to abort the fetus on week 36?",
#                                   parent_id=response["comment_id"], discussion_id=disc_id,
#                                   extra_data={"full_labels": [["CBE", "omrih"], ["OCQ", "omrih"], ["CBE", "Amir"], ["OCQ", "Amir"]], "file:line": "4rl42j_01_03:1", "subreddit_id": "t5_2w2s8", "subreddit": "changemyview", "parent_id": "t3_4rl42j", "link_id": "t3_4rl42j", "ups": 1},
#                                 actions=[], labels={"consolidated": ["CBE", "OCQ"]},
#                                     depth=2, time_stamp=1467843827, child_comments=[])
#
# comment_id = disc_con.add_comment(comment_node2)