"""Hold a generic RoboCup@Home challenge class that can be subclassed into a specific challenge.
The subclassing is done automatically based on a scoresheet"""

import re

class ScoreItem(object):
    """A ScoreItem represents a potential achievement a robot should accomplish.
    A ScoreItem (eg. recognizing something correctly) can be achieved multiple times, eg. 5x for 5 correctly recognized objects.
    The max total score is then the product of the score_per_occurence and the number of occurrences"""
    def __init__(self, description, score_per_occurence, occurrences=1):
        self.description = description
        self.score_per_occurence = score_per_occurence
        self.occurrences = occurrences

    @staticmethod
    def from_texline(texline):
        """Instantiate an ScoreItem from a line of TeX in the scoresheet macro format
        :param line a line of TeX, eg. "    \scoreitem[5]{10}{Correctly answered a question}"
        :returns ScoreItem

        >>> item = ScoreItem.from_texline("\scoreitem[5]{10}{Correctly answered a question}")
        >>> item.description
        'Correctly answered a question'
        >>> item.occurrences
        5
        >>> item.score_per_occurence
        10"""

        try:
            content = texline.strip()  # Remove whitespace
            if content.startswith("\scoreitem"):
                elements = re.findall('\{(.*?)\}', texline)
                occurrences_elements = re.findall('\[(.*?)\]', texline)
                score_per_occurence = int(elements[0])
                achievement_desc = elements[1]
                occurrences = int(occurrences_elements[0]) if occurrences_elements else 1
                return ScoreItem(achievement_desc, score_per_occurence, occurrences)
        except Exception as e:
            raise ValueError("Cannot parse '{line}': {ex}".format(line=texline, ex=e), e)

    @property
    def max_total(self):
        return self.occurrences * self.score_per_occurence

class Challenge(object):
    """A challenge is a set of achievements the robot should accomplish, baked into an overarching story"""

    def __init__(self, score_items):
        self.score_items = score_items

    @staticmethod
    def from_texfile(sheet_file):
        """
        Instantiate a Challenge from a score sheet file
        :param sheet_file: file
        :returns: Challenge

        >>> spr = Challenge.from_texfile(open("/home/loy/Dropbox/RoboCupTC/RuleBook/scoresheets/SPR.tex"))
        >>> len(spr.score_items)
        7
        >>> sum(ach.max_total for ach in spr)  # Score sheet itself says 200 but some achievements are mutually exclusive
        230
        """
        score_items = filter(None, (ScoreItem.from_texline(line) for line in sheet_file))

        return Challenge(score_items)

    def __iter__(self):
        return iter(self.score_items)


class Achievement(object):
    """Represents a robot that actually achieved/accomplished a ScoreItem

    >>> item = ScoreItem("Correctly answered a question", 10, 5)
    >>> ach_succes = Achievement(item)
    >>> ach_succes.score
    10
    """

    def __init__(self, score_item, adjusted_score=None):
        """
        :param score_item: Which ScoreItem is achieved in this Achievement
        :type score_item ScoreItem
        :param adjusted_score: if the realized score is not the score for the ScoreItem but the referee gave a customized score, that is represented here.
        """
        self.score_item = score_item
        self.adjusted_score = adjusted_score

    @property
    def score(self):
        return self.score_item.score_per_occurence if not self.adjusted_score else self.adjusted_score


class Attempt(object):
    """An attempt is, well, an attempt to complete a challenge. Most likely, not all potential achievements in a Challenge are accomplished

    >>> question = ScoreItem("Correctly answered a question", 10, 5)
    >>> face = ScoreItem("Correctly recognized face", 5, 3)
    >>> correct_question = Achievement(question)
    >>> correct_face = Achievement(face)
    >>> attempt = Attempt([correct_question, correct_face])
    >>> attempt.total_score
    15
    """

    def __init__(self, achievements):
        self.achievements = achievements

    @property
    def total_score(self):
        return sum(ach.score for ach in self.achievements)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
