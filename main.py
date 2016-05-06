import praw
import re
import random


def main():
    generator = MarkovChain()
    r = praw.Reddit(user_agent="Reddit_Json")
    submissions = r.get_subreddit('The_Donald').get_top_from_year(limit=50)
    for submission in submissions:
        print submission.title
        flat_comments = praw.helpers.flatten_tree(submission.comments)
        for comment in flat_comments:
            if hasattr(comment, "body"):
                generator.parse_text(comment.body)

    print "\n\n\n******* These are the generated sentences *******"
    for x in range(0, 100):
        print generator.generate_sentence()


class MarkovChain:
    accepted_token_regex = "[\w']+|[.,!?;]"
    punctuations = [".", "!", "?"]

    def __init__(self):
        self.dictionary = {}

    def add_word_connection(self, first_word, second_word):
        # creates a new edge if it does not currently exist
        if first_word not in self.dictionary:
            self.dictionary[first_word] = []
        # append it to the edge list
        self.dictionary[first_word].append(second_word)

    def parse_text(self, text):
        if text is "":
            assert 'Trying to parse an empty set of text'
        tokens = re.findall(self.accepted_token_regex, text)
        self.make_connections(tokens)

    def make_connections(self, tokens):
        if len(tokens) < 2:
            return
        # Makes an edge from a beginner marker to the first word of the sentence
        self.add_beginning_of_sentence(tokens[0])
        # Iterates through the tokens in pairs
        for first_word, second_word in zip(tokens[:-1], tokens[1:]):
            # Checks to see if we reached the end of the sentence
            if first_word in self.punctuations:
                self.add_beginning_of_sentence(second_word)
            else:
                self.add_word_connection(first_word, second_word)
        # Guarantees that post ends in a punctuation
        if tokens[-1] not in self.punctuations:
            self.add_word_connection(tokens[-1], ".")

    def add_beginning_of_sentence(self, word):
        self.add_word_connection("<BEGIN>", word)

    def generate_sentence(self):
        # add sentence limit
        sentence = []
        current_word = self.get_random_connection("<BEGIN>")
        sentence.append(current_word)
        while current_word not in self.punctuations:
            current_word = self.get_random_connection(current_word)
            sentence.append(current_word)
        return " ".join(sentence)

    def get_random_connection(self, word):
        if word in self.dictionary:
            return random.choice(self.dictionary[word])
        else:
            assert "There is no connection from word: " + word

if __name__ == "__main__":
    main()
