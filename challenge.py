"""Hold a generic RoboCup@Home challenge class that can be subclassed into a specific challenge.
The subclassing is done automatically based on a scoresheet"""

import re

class Achievement(object):
    """An Achievement a robot should accomplish.
    An achievement (eg. recognizing something correctly) can be achieved multiple times, eg. 5x for 5 correctly recognized objects.
    The max total score is then the product of the score_per_occurence and the number of occurrences"""
    def __init__(self, description, score_per_occurence, occurrences=1):
        self.description = description
        self.score_per_occurence = score_per_occurence
        self.occurrences = occurrences

    @staticmethod
    def from_scoreitem(texline):
        """Instantiate an Achievement from a line of TeX in the scoresheet macro format
        :param line a line of TeX, eg. "    \scoreitem[5]{10}{Correctly answered a question}"
        :returns Achievement

        >>> ach = Achievement.from_scoreitem("\scoreitem[5]{10}{Correctly answered a question}")
        >>> ach.description
        'Correctly answered a question'
        >>> ach.occurrences
        5
        >>> ach.score_per_occurence
        10"""

        try:
            content = texline.strip()  # Remove whitespace
            if content.startswith("\scoreitem"):
                elements = re.findall('\{(.*?)\}', texline)
                occurrences_elements = re.findall('\[(.*?)\]', texline)
                score_per_occurence = int(elements[0])
                achievement_desc = elements[1]
                occurrences = int(occurrences_elements[0]) if occurrences_elements else 1
                return Achievement(achievement_desc, score_per_occurence, occurrences)
        except Exception as e:
            raise ValueError("Cannot parse '{line}': {ex}".format(line=texline, ex=e), e)

    @property
    def max_total(self):
        return self.occurrences * self.score_per_occurence

class Challenge(object):
    """A challenge is a set of achievements the robot should accomplish, baked into an overarching story"""

    def __init__(self, achievements):
        self.achievements = achievements

    @staticmethod
    def from_scoresheet(sheet_file):
        """
        Instantiate a Challenge from a score sheet file
        :param sheet_file: file
        :returns: Challenge

        >>> spr = Challenge.from_scoresheet(open("/home/loy/Dropbox/RoboCupTC/RuleBook/scoresheets/SPR.tex"))
        >>> len(spr.achievements)
        7
        >>> sum(ach.max_total for ach in spr)  # Score sheet itself says 200 but some achievements are mutually exclusive
        230
        """
        achievements = filter(None, (Achievement.from_scoreitem(line) for line in sheet_file))

        return Challenge(achievements)

    def __iter__(self):
        return iter(self.achievements)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
