import random
import string

from autofixture.generators import Generator


class CustomDocumentGenerator(Generator):

    def generate(self):
        value = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15))
        return value
