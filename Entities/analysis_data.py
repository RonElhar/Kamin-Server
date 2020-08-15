

# Object that supposed to contains the Kamin analyzed data from KaminAI server when will be available
class AnalysisData:

    def __init__(self, triggering_comment):
        self.discussion_id = triggering_comment.get_discussion_id()
        self.triggered_comment = triggering_comment
        # general actions for discussion
        self.general_actions = []

        # list of actions for each comment <commentId,[actions]>
        self.comment_actions = {}

        # we probably won't need this but just in case
        self.comment_labels = {}

    def get_discussion_id(self):
        return self.discussion_id

    def set_discussion_id(self, discussion_id):
        self.discussion_id = discussion_id

    def get_triggered_comment(self):
        return self.triggered_comment

    def set_triggered_comment(self, comment):
        self.triggered_comment = comment

    def get_general_actions(self):
        return self.general_actions

    def set_general_actions(self, actions):
        self.general_actions = actions

    def add_general_action(self, action):
        self.general_actions.append(action)

    def get_comment_actions(self):
        return self.comment_actions

    def set_comment_actions(self, comments_actions):
        self.comment_actions = comments_actions

    def add_comment_actions(self, comment, actions):
        if not self.comment_actions.get(comment):
            self.comment_actions[comment] = []
        self.comment_actions[comment].append(actions)

    def get_comment_labels(self):
        return self.comment_labels

    def set_comment_labels(self, comment_labels):
        self.comment_labels = comment_labels

    def add_comment_labels(self, comment, labels):
        if not self.comment_labels.get(comment):
            self.comment_labels[comment] = []
        self.comment_labels[comment].append(labels)

    def serialize(self):
        return self.__dict__

