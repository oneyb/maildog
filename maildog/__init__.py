#!/usr/bin/env python3

from nltk import wordpunct_tokenize
from nltk.corpus import stopwords
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from jinja2 import Environment, FileSystemLoader, select_autoescape
from itertools import chain

from maildog.rulesets import _find_files

class Mail(object):
    body = None
    subject = None
    to = None
    fro = None
    reply_to = None
    html = None
    date = None
    attachments = None
    tokens = None
    language = None
    ruleset = None
    uid = None
    reply = None

    def detect_language(self):
        """
        Author: Alejandro Nolla - z0mbiehunt3r
        Purpose: detect language using a stopwords-based approach
        Created: 15/05/13
        Calculate probability of given tokens to be written in several
        languages and return the highest scored.

        It uses a stopwords based approach, counting how many unique stopwords
        are seen in analyzed text.

        @param tokens: Text whose language want to be detected
        @type tokens: str

        @return: Most scored language guessed
        @rtype: str
        """

        def _calculate_languages_ratios(words):
            """Calculate probability of given text to be written in several languages
            and return a dictionary that looks like {'french': 2, 'spanish': 4,
            'english': 0}

            @param words: Text whose language want to be detected
            @type words: str

            @return: Dictionary with languages and unique stopwords seen in
            analyzed words

            @rtype: dict

            """

            languages_ratios = {}
            # Compute per language included in nltk number of unique stopwords
            # appearing in analyzed text
            for language in stopwords.fileids():
                stopwords_set = set(stopwords.words(language))
                words_set = set(words)
                common_elements = words_set.intersection(stopwords_set)
                # language "score"
                languages_ratios[language] = len(common_elements)

            return languages_ratios

        ratios = _calculate_languages_ratios(self.tokens)

        self.language = max(ratios, key=ratios.get)

        return self.language

    def tokenize_email(self):
        text = self.subject + " " + self.body
        tokens = wordpunct_tokenize(text)
        self.tokens = [word.lower() for word in tokens]

        return self.tokens

    def choose_ruleset(self, rulesets):
        """Applies logical questions to determine what the proper answer is.
        Returns a template to be rendered with the addresses data.

        Also prepares any possible attachments for a ruleset
        @param rulesets: rules for choosing and excluding a template for answer
        @type rulesets: [namedtuple]


        @param ruleset: rules that apply to self.tokens
        @rtype ruleset: namedtuple

        """

        rulesets = [r for r in rulesets if r.language == self.language]
        ruleset_scores = [0 for i in range(len(rulesets))]
        for i, x in enumerate(rulesets):
            for token in self.tokens:
                if token in x.disqualifiers:
                    ruleset_scores[i] -= None
                    continue
                if token in x.qualifiers:
                    ruleset_scores[i] += 1

        ruleset_scores = [(r, s)
                          for r, s in zip(rulesets, ruleset_scores) if s]
        if ruleset_scores:
            (self.ruleset, _) = ruleset_scores[
                ruleset_scores.index(max(s for r, s in ruleset_scores))]
            if self.ruleset.attachments:
                self.attachments = self.ruleset.attachments.split(' ')
                return self.ruleset

    def compose_reply(self, reply_data_dir, reply_prefix='RE: '):
        """
        Put everything together into a nice reply email
        """
        assert isinstance(self.reply_to, list)

        rply = MIMEMultipart()
        rply['From'] = self.to[0]
        rply['To'] = COMMASPACE.join(self.reply_to)
        rply['Date'] = formatdate(localtime=True)
        # rply['Date'] = datetime.datetime.today().isoformat()
        rply['Subject'] = reply_prefix + self.subject
        rply["In-Reply-To"] = self.message_id
        rply["References"] = self.message_id

        rply.attach(MIMEText(self.reply))


        files = chain(*[_find_files(f, reply_data_dir)
                        for f in self.attachments])

        for f in files:
            print('Attaching: ' + f)
            with open(f, "rb") as fcon:
                p = MIMEApplication(fcon.read(), Name=basename(f))
            # After the file is closed
            p['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
            rply.attach(p)

        return rply

    def notify_owner(self, rulesets, owner):

        rply = MIMEText(self.body + '\n\n'
                        + '\n'.join(str(r._asdict()) for r in rulesets))
        rply['From'] = self.to
        rply['To'] = owner
        rply['Date'] = formatdate(localtime=True)
        # rply['Date'] = datetime.datetime.today().isoformat()
        rply['Subject'] = '[MAILDOG Unknown] RE: %s' % self.subject

        return rply

    def render_template(self, reply_template_dir):
        """
        Returns a rendered template to be sent used as email body text.
        """
        # template_path = _find_file(template, '.')
        # if not os.path.isfile(template_path):
        #     raise FileNotFoundError('Template, "%s", not found' % template)

        env = Environment(
            loader=FileSystemLoader(reply_template_dir, encoding='utf-8',
                                    followlinks=True),
            autoescape=select_autoescape(enabled_extensions=['txt', 'html']),
            auto_reload=True)

        template = env.get_template(self.ruleset[0])
        self.reply = template.render(**self.get_reply_info())
        return self.reply

    def get_reply_info(self):
        return dict(
            body=self.body,
            subject=self.subject,
            to=self.to,
            fro=self.fro,
            reply_to=self.reply_to,
            html=self.html,
            date=self.date,
            tokens=self.tokens,
            language=self.language,
            reply=self.reply,
        )

    def to_dict(self):
        return {self.uid: dict(
            body=self.body,
            subject=self.subject,
            to=self.to,
            fro=self.fro,
            reply_to=self.reply_to,
            html=self.html,
            date=self.date,
            attachments=self.attachments,
            tokens=self.tokens,
            language=self.language,
            ruleset=self.ruleset,
            reply=self.reply,
        )}
