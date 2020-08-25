"""
The goal is to convert raw pdf text into reasonably organized markdown structure,
with maximal amount of user customization permitted. The customization is provided
as config file (for now), and may evolve into a database later.

General Procedure:

Step 1: preprocessing

a. Read the config file for a specific PDF doc
b. Patch user-defined bad characters/text

Step 2: restructuring (to markdown format)

a. remove any empty lines
b. strip each line
c. concatenate non-terminating lines into paragraphs, assuming a paragraph ends with '.' 
   or ':', or the next line is the start of an unordered/ordered list. Note that this concatenation
   apply to OL and UL too
d. determine ordered/unordered lists, do not use regex, but rather a state machine.
e. insert gap lines in between paragraphs and lists

Step 3: inline-math-extraction

a. use regex to identify potential inline maths. This relies heavily on operators such as '=',
   'f(a,b)', or certain unicode math symbols, such as in, subseteq, etc.
b. process inline math into latex inline math. Substitute unicode characters with latex variables,
   for example, '\alpha', '\subseteq', but only for inline math (for now)
c. (optional) if user enables subscript detection, format subscripts as well.

Step 4: apply user patch

a. read the list of search-and-replace strings at run time (in config file?)
b. perform te user-defined replace operation
c. replace all uncommon unicode characters with latex variables, using unimap.json
"""

import os
import re
import json

def get_config_path(conf_file):
    return os.path.join(os.getcwd(), 'client', conf_file)

verbose = [ True ]

def debug(*args):
    if verbose[0]:
        print(*args)

# init global variables
with open(get_config_path("unimap.json")) as _unimap:
    unimap = json.load(_unimap)

with open(get_config_path("conf.json")) as _conf:
    _info = json.load(_conf)

with open(get_config_path("inlinemath.json")) as _imath:
    _inline_math_regex = json.load(_imath)

init_patch = _info['patch1']
inline_math_regex = _inline_math_regex
auto_subscript_enabled = True                 #TODO: read this from GUI? at run time
subscript_var = ["q", "w", "\u03b4"]     #TODO: read this from GUI? at run time
custom_patch = []                             #TODO: read this from GUI? at run time

# constants
PARAGRAPH_END = [ '.', ':' ]
OL_NUM = ["a b c", 'A B C', '1 2 3']
OL_SEP = [ r". ", r") "]
OL_BUL = [ n[0]+s for n in OL_NUM for s in OL_SEP]
UL_BUL = ['• ', '- ', '* ']
ESCAPE_SEQ = "@@@" # temperary string stub

# debugging info
debug("OL bullets:", OL_BUL)
debug("Regex for inline math:")
for r in inline_math_regex:
    debug(r)

def verify_ul(_line):
    return _line[:2] in UL_BUL

def verify_ol(_line, curr):
    if curr == None:
        return _line[:3] in OL_BUL
    else:
        return _line[:2] == chr(ord(curr[0])+1)+curr[1]

def repl_subscript(_match):
    s = _match[0]
    if len(s)==1:
        return s # unnecessary but just in case
    if len(s)==2:
        return s[0]+'_'+s[1]
    return "{}_\\{}{{{}}}".format(s[0], ESCAPE_SEQ, s[1:])

class Markdown:
    def __init__(self, raw_text):
        self.raw_text = raw_text
        self.ol = None # tracks current ordered number

    def _patch(self, _list):
        for _from, _to in _list:
            self.raw_text = self.raw_text.replace(_from, _to)

    def format_md(self):
        """ Step 1: patch bad characters """
        self._patch(init_patch)

        """ Step 2: restructuring"""
        lines = [ l.strip() for l in self.raw_text.split('\n') ]
        lines = [ l for l in lines if len(l) > 0 ]

        # concatenate all lines
        builder = ""
        self.ol = None
        for i in range(len(lines)-1):
            builder += lines[i]
            if verify_ol(lines[i+1], self.ol):
                builder += '\n'
                self.ol = lines[i+1][:2]
            elif lines[i][-1] in PARAGRAPH_END or verify_ul(lines[i+1]): # end of paragraph, newline
                builder += '\n'
                self.ol = None # reset ol state if next line not ol and eol
            else: # not end of paragraph
                builder += ' ' # do not reset ol state!!
        builder += lines[-1]

        # insert appropriate gap lines between paragraphs/uls
        lines = builder.split('\n')
        builder = ""
        i = 0
        self.ol = None
        while i < len(lines):
            # gap a block of ol
            gap = [ False, False ]
            while i < len(lines) and verify_ol(lines[i],self.ol):
                gap[0] = True
                self.ol = lines[i][:2]
                builder += '1.' + lines[i][2:] + '\n'
                i += 1
            self.ol = None
            if gap[0]:
                builder += '\n'
                gap[0] = False

            # gap a block of ul
            while i < len(lines) and verify_ul(lines[i]):
                gap[1] = True
                builder += '- ' + lines[i][2:] + '\n'
                i += 1
            if gap[1]:
                builder += '\n'
                gap[1] = False

            # gap a regular paragraph
            if i < len(lines) and not verify_ol(lines[i],self.ol):
                builder += lines[i] + '\n\n'
                i += 1
        self.raw_text = builder

        """ Step 3: inline-math-extraction"""
        inline_math_patch=set()
        for r in inline_math_regex:
            for m in re.finditer(r, builder):
                detected = m[0]
                stuffing = [ False ]
                if detected[0] == ' ':
                    stuffing[0] = True

                # escape latex-sensitive characters
                formatted = detected.replace('{','\\{').replace('}','\\}').replace('#', '\\#')

                # handle subscript
                if auto_subscript_enabled:
                    var_sub_exprs = [ re.compile(r"{}((?!{})[A-Za-zΑ-Ωα-ω\d\+\-])+".format(v,v)) for v in subscript_var ]
                    for var_sub in var_sub_exprs:
                        formatted = var_sub.sub(repl_subscript, formatted)

                # substitute latex variables to get rid of trailing whitespace
                for k in unimap:
                    formatted = formatted.replace(k, unimap[k] + ' ')
                formatted = "$"+formatted.strip().replace(ESCAPE_SEQ, 'mathrm') + "$"

                if stuffing[0]:
                    formatted = ' '+formatted
                inline_math_patch.add((detected, formatted))
        self._patch(inline_math_patch)
        
        
        """ Step 4: apply user patch"""
        self._patch(custom_patch)
        self._patch((k, unimap[k]) for k in unimap)

        return self.raw_text        
        # with open('test.txt', mode='w+', encoding="utf-8") as f:
        #     f.write(self.raw_text)




## Testing Area
if __name__ == "__main__":
    Markdown("""
80 CHAPTER 1 / REGULAR LANGUAGES
To use the pumping lemma to prove that a language B is not regular, first as-
sume that B is regular in order to obtain a contradiction. Then use the pumping
lemma to guarantee the existence of a pumping length p such that all strings of
length p or greater in B can be pumped. Next, find a string s in B that has length
p or greater but that cannot be pumped. Finally, demonstrate that s cannot be
pumped by considering all ways of dividing s into x, y, and z (taking condition 3
of the pumping lemma into account if convenient) and, for each such division,
finding a value i where xyi
z 6∈ B. This final step often involves grouping the
various ways of dividing s into several cases and analyzing them individually.
The existence of s contradicts the pumping lemma if B were regular. Hence B
cannot be regular.
Finding s sometimes takes a bit of creative thinking. You may need to hunt
through several candidates for s before you discover one that works. Try mem-
bers of B that seem to exhibit the “essence” of B’s nonregularity. We further
discuss the task of finding s in some of the following examples.
EXAMPLE 1.73

Let B be the language {0n
1n
|n ≥ 0}. We use the pumping lemma to prove that
B is not regular. The proof is by contradiction.
Assume to the contrary that B is regular. Let p be the pumping length given
by the pumping lemma. Choose s to be the string 0p
1p

. Because s is a member
of B and s has length more than p, the pumping lemma guarantees that s can be
split into three pieces, s = xyz, where for any i ≥ 0 the string xyi
z is in B. We

consider three cases to show that this result is impossible.
1. The string y consists only of 0s. In this case, the string xyyz has more 0s
than 1s and so is not a member of B, violating condition 1 of the pumping
lemma. This case is a contradiction.
2. The string y consists only of 1s. This case also gives a contradiction.
3. The string y consists of both 0s and 1s. In this case, the string xyyz may
have the same number of 0s and 1s, but they will be out of order with some
1s before 0s. Hence it is not a member of B, which is a contradiction.
Thus a contradiction is unavoidable if we make the assumption that B is reg-
ular, so B is not regular. Note that we can simplify this argument by applying
condition 3 of the pumping lemma to eliminate cases 2 and 3.
In this example, finding the string s was easy because any string in B of
length p or more would work. In the next two examples, some choices for s
do not work so additional care is required.
EXAMPLE 1.74

Let C = {w| w has an equal number of 0s and 1s}. We use the pumping lemma
to prove that C is not regular. The proof is by contradiction.
Copyright 2012 Cengage Learning. All Rights Reserved. May not be copied, scanned, or duplicated, in whole or in part. Due to electronic rights, some third party content may be suppressed from the
eBook and/or eChapter(s). Editorial review has deemed that any suppressed content does not materially affect the overall learning experience. Cengage Learning reserves the right to remove additional
content at any time if subsequent rights restrictions require it.

3.1 TURING MACHINES 173
EXAMPLE 3.9
The following is a formal description of M1 = (Q, Σ, Γ, δ, q1, qaccept, qreject), the
Turing machine that we informally described (page 167) for deciding the lan-
guage B = {w#w| w ∈ {0,1}∗
}.
• Q = {q1, . . . , q8, qaccept, qreject},
• Σ = {0,1,#}, and Γ = {0,1,#,x, }.
• We 
describe 
δ with a
state
diagram (see the following figure).
• The start, accept, and reject states are q1, 
qaccept, and qreject, respectively.
FIGURE 3.10
State diagram for Turing machine M1
In Figure 3.10, which depicts the state diagram of TM M1, you will find the
label 0,1→R on the transition going from q3 to itself. That label means that the
machine stays in q3 and moves to the right when it reads a 0 or a 1 in state q3. It
doesn’t change the symbol on the tape.
Stage 1 is implemented by states q1 through q7, and stage 2 by the remaining
states. To simplify the figure, we don’t show the reject state or the transitions
going to the reject state. Those transitions occur implicitly whenever a state
lacks an outgoing transition for a particular symbol. Thus because in state q5
no outgoing arrow with a # is present, if a # occurs under the head when the
machine is in state q5, it goes to state qreject. For completeness, we say that the
head moves right in each of these transitions to the reject state.
Copyright 2012 Cengage Learning. All Rights Reserved. May not be copied, scanned, or duplicated, in whole or in part. Due to electronic rights, some third party content may be suppressed from the
eBook and/or eChapter(s). Editorial review has deemed that any suppressed content does not materially affect the overall learning experience. Cengage Learning reserves the right to remove additional
content at any time if subsequent rights restrictions require it.

a. test
test
b. test test 
test
c. test


3.1

EXAMPLE

TURING MACHINES

173

3.9

The following is a formal description of M1 = (Q, Σ, Γ, δ, q1 , qaccept , qreject ), the
Turing machine that we informally described (page 167) for deciding the language B = {w#w| w ∈ {0,1}∗ }.
•

Q = {q1 , . . . , q8 , qaccept , qreject },

•

Σ = {0,1,#}, and Γ = {0,1,#,x, }.

•

We describe δ with a state diagram (see the following figure).

•

The start, accept, and reject states are q1 , qaccept , and qreject , respectively.

FIGURE 3.10
State diagram for Turing machine M1
In Figure 3.10, which depicts the state diagram of TM M1 , you will find the
label 0,1→R on the transition going from q3 to itself. That label means that the
machine stays in q3 and moves to the right when it reads a 0 or a 1 in state q3 . It
doesn’t change the symbol on the tape.
Stage 1 is implemented by states q1 through q7 , and stage 2 by the remaining
states. To simplify the figure, we don’t show the reject state or the transitions
going to the reject state. Those transitions occur implicitly whenever a state
lacks an outgoing transition for a particular symbol. Thus because in state q5
no outgoing arrow with a # is present, if a # occurs under the head when the
machine is in state q5 , it goes to state qreject . For completeness, we say that the
head moves right in each of these transitions to the reject state.

Copyright 2012 Cengage Learning. All Rights Reserved. May not be copied, scanned, or duplicated, in whole or in part. Due to electronic rights, some third party content may be suppressed from the
eBook and/or eChapter(s). Editorial review has deemed that any suppressed content does not materially affect the overall learning experience. Cengage Learning reserves the right to remove additional
content at any time if subsequent rights restrictions require it.


    """).format_md()

# class RawTextProcessor:
#     def __init__(self):
        