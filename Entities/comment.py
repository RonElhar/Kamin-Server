from datetime import datetime


# Comment object contains all the details of the comment creation, who is the author and for who it replied, the depth
# and timestamp attributes allowing the client to now where to place the comment in the presented discussion.
# The type of the comment can be comment - for regular comments between users, alert - for moderator alerts and
# config - for configuration changes during the discussion
class Comment:

    def __init__(self, *args, **kwargs):
        self._id = None
        self.author = kwargs.get('author', '')
        self.text = kwargs.get('text', '')
        self.parent_id = kwargs.get('parent_id', '')
        self.discussion_id = kwargs.get('discussion_id', '')
        self.extra_data = kwargs.get('extra_data', {})
        self.depth = kwargs.get('depth', 0)
        self.timestamp = kwargs.get('timestamp', datetime.now().timestamp())
        self.comment_type = kwargs.get('comment_type', 'comment')

    def get_id(self):
        return self._id

    def set_id(self, input_id):
        self._id = input_id

    def get_author(self):
        return self.author

    def set_author(self, name):
        self.author = name

    def get_text(self):
        return self.text

    def set_text(self, input_text):
        self.text = input_text

    def get_parent_id(self):
        return self.parent_id

    def set_parent_id(self, parent_id):
        self.parent_id = parent_id

    def get_discussion_id(self):
        return self.discussion_id

    def set_discussion_id(self, input_id):
        self.discussion_id = input_id

    def get_depth(self):
        return self.depth

    def set_depth(self, input_depth):
        self.depth = input_depth

    def get_timestamp(self):
        return self.timestamp

    def set_timestamp(self, input_timestamp):
        self.timestamp = input_timestamp

    def get_extra_data(self):
        return self.extra_data

    def set_extra_data(self, extra_data):
        self.extra_data = extra_data

    def get_comment_type(self):
        return self.comment_type

    def set_comment_type(self, comment_type):
        self.comment_type = comment_type

    def get_depth_space(self):
        space = ""
        for i in range(1, self.get_depth()):
            space += "      "
        return space

    def __str__(self):
        return self.get_depth_space() + str(self._id) + ", " + self.author + ": " + str(
            self.get_timestamp()) + ", depth = " + str(self.get_depth()) + ", parent id = " + str(
            self.parent_id)


# The CommentNode contains the child_comments list, that relates a comment for all her sub comments in the discussion
class CommentNode(Comment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._id = kwargs.get('id', "")
        self.child_comments = kwargs.get('child_comments', [])

    def add_child_comment(self, comment):
        self.child_comments.append(comment)

    def get_child_comments(self):
        return self.child_comments

    def set_child_comments(self, children):
        self.child_comments = children

    def to_db_dict(self):
        return {
            "author": self.author,
            "text": self.text,
            "parentId": self.parent_id,
            "discussionId": self.discussion_id,
            "depth": self.depth,
            "timestamp": self.timestamp,
            "extra_data": self.extra_data,
            "child_comments": self.child_comments,
            "comment_type": self.comment_type
        }

    def to_client_dict(self):
        return {
            "id": self._id,
            "author": self.author,
            "text": self.text,
            "parentId": self.parent_id,
            "discussionId": self.discussion_id,
            "depth": self.depth,
            "timestamp": self.timestamp,
            "extra_data": self.extra_data,
            "comment_type": self.comment_type
        }

    def to_csv_record(self):
        return [
            self._id,
            self.author,
            self.text,
            self.parent_id,
            self.discussion_id,
            self.depth,
            self.timestamp,
            self.extra_data,
            self.comment_type
            ]
