import pymongo
from bson.objectid import ObjectId
from datetime import datetime
import db_config

# The DBManagement class is responsible for all the connections to the DB

# The MongoDB client details are configured in the file db_config.config
# For saving the credentials you must have this file locally or in the deploy server but not push it to the GitHub.
client = pymongo.MongoClient(db_config.config)

# The cluster and all the tables used are define here and created automaticly if dont exist in the DB
kamin_db = client["kamindb"]
discussion_col = kamin_db["discussion"]
comment_col = kamin_db["comment"]
user_col = kamin_db["user"]
user_discussion_statistics_col = kamin_db["userDiscussionStatistics"]
user_discussion_configuration_col = kamin_db["userDiscussionConfiguration"]


class DBManagement:
    kamin_db = client["kamindb"]
    discussion_col = kamin_db["discussion"]
    comment_col = kamin_db["comment"]
    user_col = kamin_db["user"]
    user_discussion_statistics_col = kamin_db["userDiscussionStatistics"]
    user_discussion_configuration_col = kamin_db["userDiscussionConfiguration"]

    # Add a new discussion from discussion object to the discussions table at the DB
    def create_discussion(self, discussion):
        result = self.discussion_col.insert_one(discussion.to_dict())
        discussion.set_id(result.inserted_id.binary.hex())
        return result.inserted_id.binary.hex()

    # Returns a list of all the discussion ids of the simulations discussion or real time discussions
    # according to is_simulation parameter
    def get_discussions(self, is_simulation):
        discussions = self.discussion_col.find({"is_simulation": is_simulation})
        discussions_list = {}
        for discussion in discussions:
            discussions_list[discussion["_id"].binary.hex()] = discussion["title"]
        return discussions_list

    # Returns a discussion and comments dictionary of all the comments that belongs to the discussion_id if exist
    def get_discussion(self, discussion_id):
        discussion = self.discussion_col.find_one({"_id": ObjectId(discussion_id)})
        comments = self.comment_col.find({"discussionId": discussion_id})
        comments_dict = {}
        for comment in comments:
            comments_dict[comment["_id"].binary.hex()] = comment
        return discussion, comments_dict

    # Returns the discussion dictionary of discussion_id if exist
    def get_discussion_details(self, discussion_id):
        discussion = self.discussion_col.find_one({"_id": ObjectId(discussion_id)})
        return discussion

    # Add new comment from a comment object to the comments table in DB,
    # update statistics of user and discussion in the relevant tables
    def add_comment(self, comment):
        comment.set_timestamp(datetime.now().timestamp())
        result = self.comment_col.insert_one(comment.to_db_dict())
        comment_id = result.inserted_id.binary.hex()
        comment.set_id(comment_id)
        discussion = self.discussion_col.find_one({"_id": ObjectId(comment.get_discussion_id())})
        if discussion["root_comment_id"] is None:
            discussion_col.update_one({"_id": ObjectId(comment.get_discussion_id())},
                                      {"$set": {"root_comment_id": comment_id}})

        if comment.get_parent_id() is not None:
            parent_comment = self.comment_col.find_one({"_id": ObjectId(comment.get_parent_id())})
            child_ids = parent_comment["child_comments"]
            child_ids.append(comment.get_id())
            comment_col.update_one({"_id": ObjectId(comment.get_parent_id())}, {"$set": {"child_comments": child_ids}})
            # user statistics
            if comment.get_comment_type() == "comment":
                self.update_user_statistics(comment)

        # discussion statistics
        if comment.get_comment_type() == "comment":
            self.update_discussion_statistics(comment.get_discussion_id())
        return result.inserted_id.binary.hex()

    # Update the user statistics according to the new comment he wrote
    def update_user_statistics(self, comment):
        if comment.get_comment_type() is not "comment":
            return
        commented_users = {}
        username = comment.get_author()
        statistics = self.user_discussion_statistics_col.find_one({"username": username,
                                                                   "discussion_id": comment.get_discussion_id()})
        if comment.get_parent_id() is not None:
            # author statistics
            parent_username = self.get_author_of_comment(comment.get_parent_id())
            commented_users = statistics["commented_users"]
            if commented_users.__contains__(parent_username):
                commented_users[parent_username] += 1
            else:
                commented_users[parent_username] = 1

            # parent statistics
            parent_statistics = self.user_discussion_statistics_col.find_one({"username": parent_username,
                                                                              "discussion_id": comment.get_discussion_id()})
            responded_users = parent_statistics["responded_users"]
            if responded_users.__contains__(username):
                responded_users[username] += 1
            else:
                responded_users[username] = 1
            self.user_discussion_statistics_col.update_one({"_id": ObjectId(parent_statistics["_id"])},
                                                           {"$set": {"responded_users": responded_users}})

        # num of words statistics
        num_of_words = len(comment.get_text().split())
        total_words = statistics["total_words_num"]
        total_words += num_of_words
        self.user_discussion_statistics_col.update_one({"_id": ObjectId(statistics["_id"])},
                                                       {"$set": {"commented_users": commented_users,
                                                                 "total_words_num": total_words}})

    # Update the total comments num of discussion_id
    def update_discussion_statistics(self, discussion_id):
        # discussion statistics
        discussion = self.get_discussion_details(discussion_id)
        total_comments_num = discussion["total_comments_num"]
        self.update_discussion(discussion_id, "total_comments_num", total_comments_num + 1)

    # Get the statistics of user in a discussion from the user_discussion_statistics table in DB
    def get_user_discussion_statistics(self, username, discussion_id):
        statistics = self.user_discussion_statistics_col.find_one(
            {"username": username, "discussion_id": discussion_id})
        if statistics is not None:
            total_words = statistics["total_words_num"]
            commented_users = dict(statistics["commented_users"])
            num_of_commented_users = len(commented_users.keys())
            num_of_comments = sum(commented_users.values())
            responded_users = dict(statistics["responded_users"])
            num_of_responded_users = len(responded_users.keys())
            num_of_responses = sum(responded_users.values())
            user_statistics = {"total_words": total_words, "num_of_commented_users": num_of_commented_users,
                               "num_of_comments": num_of_comments, "num_of_responded_users": num_of_responded_users,
                               "num_of_responses": num_of_responses}
            statistics = user_statistics
        return statistics

    # Get the statistics of discussion from the user_discussion_statistics table in DB
    def get_discussion_statistics(self, discussion_id):
        discussion_statistics = None
        statistics_list = self.user_discussion_statistics_col.find({"discussion_id": discussion_id})
        if statistics_list is not None and statistics_list.count() > 0:
            max_commented_user = ""
            max_commented_num = 0
            max_responded_user = ""
            max_responded_num = 0
            discussion = self.get_discussion_details(discussion_id)
            num_of_participants = discussion["num_of_participants"]
            total_comments_num = discussion["total_comments_num"]
            for user_statistics in statistics_list:
                commented_users = dict(user_statistics["commented_users"])
                if len(commented_users.keys()) > max_commented_num:
                    max_commented_user = user_statistics["username"]
                    max_commented_num = len(commented_users.keys())
                responded_users = dict(user_statistics["responded_users"])
                if len(responded_users.keys()) > max_responded_num:
                    max_responded_user = user_statistics["username"]
                    max_responded_num = len(responded_users.keys())
            discussion_statistics = {"max_commented_user": max_commented_user, "max_commented_num": max_commented_num,
                                     "max_responded_user": max_responded_user, "max_responded_num": max_responded_num,
                                     "num_of_participants": num_of_participants,
                                     "total_comments_num": total_comments_num}
        return discussion_statistics

    # Update attributes in the discussions table
    def update_discussion(self, discussion_id, col_to_set, updated_value):
        result = self.discussion_col.update_one({"_id": ObjectId(discussion_id)}, {"$set": {col_to_set: updated_value}})
        return result.acknowledged

    # Add new statistics record for user in discussion
    def add_user_discussion_statistics(self, username, discussion_id):
        result = self.get_user_discussion_statistics(username, discussion_id)
        if result is None:
            self.user_discussion_statistics_col.insert_one({"username": username,
                                                            "discussion_id": discussion_id,
                                                            "commented_users": {}, "responded_users": {},
                                                            "total_words_num": 0})
            disc_data = self.discussion_col.find_one({"_id": ObjectId(discussion_id)})
            self.update_discussion(discussion_id, "num_of_participants", disc_data["num_of_participants"] + 1)
        return

    # Add new configuration record for user in discussion
    def add_user_discussion_configuration(self, user, discussion_id, vis_config):
        result = self.get_user_discussion_configuration(user.get_user_name(), discussion_id)
        if result is None and user.get_permission() == 1:
            self.user_discussion_configuration_col.insert_one({"username": user.get_user_name(),
                                                               "discussion_id": discussion_id,
                                                               "config": vis_config})
        return

    # Update presented configurations for user in discussion
    def update_user_discussion_configuration(self, username, discussion_id, new_config):
        configuration = self.user_discussion_configuration_col.find_one(
            {"discussion_id": discussion_id, "username": username})
        if configuration is not None:
            configuration = dict(configuration)
            for config in new_config:
                configuration[config] = new_config[config]
            self.user_discussion_configuration_col.update_one({"_id": ObjectId(configuration["_id"])},
                                                              {"$set": {"config": new_config}})

    # Get configuration details of user in discussion
    def get_user_discussion_configuration(self, username, discussion_id):
        configuration = self.user_discussion_configuration_col.find_one(
            {"discussion_id": discussion_id, "username": username})
        if configuration is not None:
            configuration = {"configuration": configuration["config"]}
        return configuration

    # Get all the users configurations details of discussion_id
    def get_all_users_discussion_configurations(self, discussion_id):
        users_configuration = {}
        configurations = self.user_discussion_configuration_col.find({"discussion_id": discussion_id})
        for config in configurations:
            users_configuration[config["username"]] = config["config"]
        return users_configuration

    # Get a comment dictionary of comment_id
    def get_comment(self, comment_id):
        comment = self.comment_col.find_one({"_id": ObjectId(comment_id)})
        return comment

    # Add new user record to Users table in the DB from user object
    def add_new_user(self, user):
        result = self.user_col.insert_one(user.to_dict())
        return result.inserted_id.binary.hex()

    # Get user details of username from the users table in DB
    def get_user(self, username):
        user = self.user_col.find_one({"user_name": username})
        return user

    # Get the username of the author of comment_id
    def get_author_of_comment(self, comment_id):
        comment = self.comment_col.find_one({"_id": ObjectId(comment_id)})
        return comment["author"]

    # Get two lists, contains all users, one for regular users, one for moderators users
    def get_users(self):
        users = []
        moderators = []
        for user in self.user_col.find():
            if user["permission"] == 1:
                users.append(user["user_name"])
            if user["permission"] == 2:
                moderators.append(user["user_name"])
        return users, moderators

    # Update user permission of user to the permission received
    def change_user_permission(self, user, permission):
        result = self.user_col.update_one({"_id": ObjectId(user.get_user_id())}, {"$set": {"permission": permission}})
        return result.acknowledged

    # Get the discussion creator
    def get_discussion_moderator(self, discussion_id):
        discussion = self.discussion_col.find_one({"_id": ObjectId(discussion_id)})
        root_comment_id = discussion["root_comment_id"]
        moderator = self.get_author_of_comment(root_comment_id)
        return moderator

    # Delete all the discussion configurations from the DB when discussion is ended
    def delete_discussion_configurations(self, discussion_id):
        self.user_discussion_configuration_col.delete_many({"discussionId": discussion_id})

    # Get all the users that added at least one comment in the discussion and can be alerted
    def get_responded_users(self, discussion_id):
        comments = self.comment_col.find({"discussionId": discussion_id})
        responded_users = []
        for comment in comments:
            responded_users.append(comment['author'])
        return set(responded_users)
