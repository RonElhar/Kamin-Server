import pandas as pd


# Discussion object contains all the details of tha discussion initialization and statistics that updated during the
# real time conversation, when the discussion became to simulation the attribute is_simulation will change to true
# The discussion contains the root_comment_id, the detail the relates it for the conversation tree
class Discussion:

    def __init__(self, *args, **kwargs):
        self.discussion_id = kwargs.get('id', 0)
        self.title = kwargs.get('title', "")
        self.categories = kwargs.get('categories', [])
        self.root_comment_id = kwargs.get('root_comment_id', 0)
        self.num_of_participants = kwargs.get('num_of_participants', 0)
        self.total_comments_num = kwargs.get('total_comments_num', 0)
        self.total_alerts_num = kwargs.get('total_alerts_num', 0)  # Do not change this!!! important for simulation
        self.is_simulation = kwargs.get('is_simulation', False)
        self.configuration = kwargs.get('configuration', {"vis_config": {"graph": True, "alerts": True,
                                                                         "statistics": True},
                                                          "extra_config": {}})

    def get_id(self):
        return self.discussion_id

    def set_id(self, discussion_id):
        self.discussion_id = discussion_id

    def get_title(self):
        return self.title

    def set_title(self, title):
        self.title = title

    def get_categories(self):
        return self.categories

    def set_categories(self, input_categories):
        self.categories = input_categories

    def get_root_comment_id(self):
        return self.root_comment_id

    def set_root_comment_id(self, comment_id):
        self.root_comment_id = comment_id

    def get_num_of_participants(self):
        return self.num_of_participants

    def set_num_of_participants(self, num_of_participants):
        self.num_of_participants = num_of_participants

    def get_total_comments_num(self):
        return self.total_comments_num

    def set_total_comments_num(self, total_comments_num):
        self.total_comments_num = total_comments_num

    def get_is_simulation(self):
        return self.is_simulation

    def set_is_simulation(self, is_simulation):
        self.is_simulation = is_simulation

    def get_configuration(self):
        return self.configuration

    def set_configuration(self, configuration):
        self.configuration = configuration

    def to_dict(self):
        return {
            'categories': self.categories,
            'title': self.title,
            'root_comment_id': self.root_comment_id,
            'num_of_participants': self.num_of_participants,
            'total_comments_num': self.total_comments_num,
            'is_simulation': self.is_simulation,
            'configuration': self.configuration
        }


# The DiscussionTree contains the root_comment object (and not the id string of it) , it relates the discussion to the
# conversation tree that starts from the root comment
class DiscussionTree(Discussion):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root_comment = kwargs.get('root_comment', None)

    def get_root_comment(self):
        return self.root_comment

    def set_root_comment(self, comment):
        self.root_comment = comment

    def to_json_dict(self):
        discussion = self.to_dict()
        discussion_json_tree = tree_to_json(self.root_comment)
        return {'discussion': discussion, 'tree': discussion_json_tree}

    # Write the discussionTree to csv file
    def to_csv(self):
        records = []
        first_record = self.root_comment.to_csv_record()
        i = 1
        first_record.insert(3, "")
        first_record.insert(5, str(0))
        records.append(first_record)
        target_author = self.root_comment.author
        for child in self.root_comment.child_comments:
            to_csv_record_list(child, target_author, i, None, records)
        df = pd.DataFrame(records,
                          columns=["id", "author", "text", "target user", "parent_id", "branch id", "discussion id",
                                   "depth",
                                   "timestamp", "extra_data", "comment_type"])

        return df.to_csv()

    # Add new comment to the right position in the tree
    def add_comment(self, comment):
        self.add_comment_recursive(self.root_comment, comment)
        if comment.comment_type != "comment":
            self.total_alerts_num += 1

    def add_comment_recursive(self, current_node, comment):
        if current_node.get_id() == comment.get_parent_id():
            current_node.add_child_comment(comment)
            return

        [self.add_comment_recursive(child, comment) for child in current_node.get_child_comments()]


def tree_to_json(comment_node):
    return {'node': comment_node.to_client_dict(),
            'children': [tree_to_json(child) for child in comment_node.get_child_comments()]}


def to_csv_record_list(comment_node, target_author, parent_branch, child_index, records):
    branch_id = str(parent_branch) + '.' + str(child_index) if child_index else str(parent_branch)
    csv_record = comment_node.to_csv_record()
    csv_record.insert(3, target_author)
    csv_record.insert(5, branch_id)
    records.append(csv_record)
    target_author = comment_node.author
    i = 1
    for child in comment_node.child_comments:
        to_csv_record_list(child, target_author, branch_id, i, records)
        i += 1
