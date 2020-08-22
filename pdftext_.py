#%%
import re

"""Operations
0. Extract text with pdftotext tool, using utf-8 encoding;
0.2 read user-defined config files
1. Patch user-defined bad text, preprocessing (double \\n)
2. Separate out UL and OL
3. Use regex to discover inline formulas, format inline formulas and patch subscriptable variables
4. Apply user patch (optional)
"""

stub_patch = { # from, to
    ('ﬁ', 'fi'),
    ('. . .', '...'),
    ('where ∈ Γ', 'where ⊔ ∈ Γ')
}

subscript_var = ['q', 'w', 'δ', 'r']

auto_subscript_enabled = True
_debug = True

stub_raw_text = """
3.1 TURING MACHINES 173
EXAMPLE 3.9 The following is a formal description of M1 = (Q, Σ, Γ, δ, q1, qaccept, qreject), the Turing machine that we informally described (page 167) for deciding the language B = {w#w| w ∈ {0,1}∗}.
• Q = {q1, . . . , q8, qaccept, qreject}, • Σ = {0,1,#}, and Γ = {0,1,#,x, }. • We describe δ with a state diagram (see the following ﬁgure). • The start, accept, and reject states are q1, qaccept, and qreject, respectively.
FIGURE 3.10 State diagram for Turing machine M1
In Figure 3.10, which depicts the state diagram of TM M1, you will ﬁnd the label 0,1→R on the transition going from q3 to itself. That label means that the machine stays in q3 and moves to the right when it reads a 0 or a 1 in state q3. It doesn’t change the symbol on the tape.
Stage 1 is implemented by states q1 through q7, and stage 2 by the remaining states. To simplify the ﬁgure, we don’t show the reject state or the transitions going to the reject state. Those transitions occur implicitly whenever a state lacks an outgoing transition for a particular symbol. Thus because in state q5 no outgoing arrow with a # is present, if a # occurs under the head when the machine is in state q5, it goes to state qreject. For completeness, we say that the head moves right in each of these transitions to the reject state.
Copyright 2012 Cengage Learning. All Rights Reserved. May not be copied, scanned, or duplicated, in whole or in part. Due to electronic rights, some third party content may be suppressed from the eBook and/or eChapter(s). Editorial review has deemed that any suppressed content does not materially affect the overall learning experience. Cengage Learning reserves the right to remove additional
content at any time if subsequent rights restrictions require it.
"""

# Step 0: read text
raw_text = stub_raw_text                     ###### TODO: obtain the raw text from clipboard?

# Step 1: patch user-defined bad text
patch = stub_patch                           ###### TODO: read from custom patch file
for _from, _to in patch:
    raw_text = raw_text.replace(_from, _to)
raw_text = raw_text.replace('\n','\n\n')

# Step 2-: separate OL from raw_text
ol_orders = ["a b c", 'A B C', '1 2 3'] # used for generating regex
seps = [ r"\. ", r"\) "]            # used for generating regex
MIN_ROW_LEN = 8

# regex generation
ol_regex = [] # !!!****IMPORTANT****: assume ordered list is aggregated into 1 line after text extraction
for order_str in ol_orders:
    for sep in seps:
        regex_str = ""
        for letter in order_str.split():
            regex_str += "({}{}.{{{}}}.+?)".format(letter,sep,MIN_ROW_LEN)
        regex_str += r"\n"
        ol_regex.append((order_str, sep, regex_str))

print("ordered_list")
for reg in ol_regex:
    print(reg[2])

replacements = [] # (from, to)
for ol,sep,r in ol_regex:
    for m in re.finditer(r, raw_text):
        _ol = m[0]
        i = ord(ol[0])
        prev = None
        curr = _ol
        while curr != prev:
            prev = curr
            #print(chr(i)+sep.replace('\\','')+"|")
            curr = curr.replace(chr(i)+sep.replace('\\',''), '\n1. ', 1)
            #print(prev, curr)
            i += 1
        replacements.append((m[0], '\n'+curr+'\n'))
#print(replacements)
for _from, _to in replacements:
    raw_text = raw_text.replace(_from, _to)
print("<----------end-OL-replacement")

bullets = ['• ', '\\- ', '\\* ']
ul_regex = []

for bullet in bullets:
    ul_regex.append((bullet, 
        "({}.+?)({}.+?).+\n".format(bullet,bullet)))
for _,reg in ul_regex:
    print(reg)

replacements = [] # (from, to)
for bullet, r in ul_regex:
    for m in re.finditer(r, raw_text):
        replacements.append((m[0], m[0].replace(bullet.replace('\\',''), "\n- ")))

for _from, _to in replacements:
    raw_text = raw_text.replace(_from, _to)
raw_text = raw_text.replace('• ', '- ') # hard-coded, don't worry about it
print(replacements)
print("<----------end-UL-replacement")

#print(raw_text)

# ol_var1=r"(1\. .{{{}}}.+?)(2\. .{{{}}}.+?)(3\. .{{{}}}.+?)\n".format(
#     MIN_ROW_LEN,MIN_ROW_LEN,MIN_ROW_LEN)
# ol_var2=r"(1\. .{{{}}}.+?)(2\. .{{{}}}.+?)(3\. .{{{}}}.+?)\n".format(
#     MIN_ROW_LEN,MIN_ROW_LEN,MIN_ROW_LEN)

# Step 3: patching in-line formulas
english="[a-zA-Z]"
greek="[α-ωΑ-Ω]"

#bracket_expression=r"\(([A-Za-zΑ-Ωα-ω\d ]{1,9},)+[A-Za-zΑ-Ωα-ω\d ]{1,9}\)"
#func_expression=r" [A-Za-zΑ-Ωα-ω]{1,4}\d{0,4}\(([A-Za-zΑ-Ωα-ω\d ]{1,9}, ?)*[A-Za-zΑ-Ωα-ω\d]{1,9}\)"
func_expression=r" [A-Za-zΑ-Ωα-ω]{1,4}\d{0,4}\(.+?\)"
other_binary_expr=r"([A-Za-zΑ-Ωα-ω\d]{1,8}, ?)*[A-Za-zΑ-Ωα-ω\d]{1,8} ?[∈⊆] ?[A-Za-zΑ-Ωα-ω\d]+"
#func_def_expr_1= "[A-Za-zΑ-Ωα-ω\d]{1,4} ?: ?.+?−→ ?.+?(\{.+?\}|\(.+?\))"
gen_expr=r"((\(.+?\)|\[.+?\]|\{.+?\}|[A-Za-zΑ-Ωα-ω\d]{1,8}) ?[×+\-\/\*] ?)*(\(.+?\)|\[.+?\]|\{.+?\}|[A-Za-zΑ-Ωα-ω\d]{1,8})" # don't capture this directly
func_def_expr_2= r"[A-Za-zΑ-Ωα-ω\d]{1,4} ?: ?.+?−→ ?" + gen_expr
var_ass_expr=r"[A-Za-zΑ-Ωα-ω\d]{1,9} ?= ?" + gen_expr
func_ass_expr=func_expression+" ?= ?"+gen_expr
var_list_expr=r"([A-Za-zΑ-Ωα-ω\d]{1,9}, ?)*[A-Za-zΑ-Ωα-ω\d]{1,9}"

inline_regex = [
    other_binary_expr,
    func_def_expr_2,
    var_ass_expr,
    func_ass_expr
    ]

import json
print(json.dumps(inline_regex, indent=2))

if _debug:
    for reg in inline_regex:
        print(reg)

unimap = {
    chr(8838): r"\subseteq",
    chr(8722)+chr(8594): r"\rightarrow",
    chr(8712): r'\in',
    chr(215): r'\times',
    chr(8852): r'\sqcup',
    chr(0x03b1): r'\alpha',
    chr(0x0391): r'\Alpha',
    chr(0x03b2): r'\beta',
    chr(0x0392): r'\Beta',
    chr(0x03b3): r'\gamma',
    chr(0x0393): r'\Gamma',
    chr(0x03b4): r'\delta',
    chr(0x0394): r'\Delta',
    chr(0x03b5): r'\epsilon',
    chr(0x0395): r'\Epsilon',
    chr(0x03b6): r'\zeta',
    chr(0x0396): r'\Zeta',
    chr(0x03b7): r'\eta',
    chr(0x0397): r'\Eta',
    chr(0x03b8): r'\theta',
    chr(0x0398): r'\Theta',
    chr(0x03b9): r'\iota',
    chr(0x0399): r'\Iota',
    chr(0x03ba): r'\kappa',
    chr(0x039a): r'\Kappa',
    chr(0x03bb): r'\lambda',
    chr(0x039b): r'\Lambda',
    chr(0x03bc): r'\mu',
    chr(0x039c): r'\Mu',
    chr(0x03bd): r'\nu',
    chr(0x039d): r'\Nu',
    chr(0x03be): r'\xi',
    chr(0x039e): r'\Xi',
    chr(0x03bf): r'\omicron',
    chr(0x039f): r'\Omicron',
    chr(0x03c0): r'\pi',
    chr(0x03a0): r'\Pi',
    chr(0x03c1): r'\rho',
    chr(0x03a1): r'\Rho',
    chr(0x03c3): r'\sigma',
    chr(0x03a3): r'\Sigma',
    chr(0x03c4): r'\tau',
    chr(0x03a4): r'\Tau',
    chr(0x03c5): r'\upsilon',
    chr(0x03a5): r'\Upsilon',
    chr(0x03c6): r'\phi',
    chr(0x03a6): r'\Phi',
    chr(0x03c7): r'\chi',
    chr(0x03a7): r'\Chi',
    chr(0x03c8): r'\psi',
    chr(0x03a8): r'\Psi',
    chr(0x03c9): r'\omega',
    chr(0x03a9): r'\Omega'
}

ESCAPE_SEQ="@@@"
def repl_subscript(_match):
    s = _match[0]
    if len(s)==1:
        return s # unnecessary but just in case
    if len(s)==2:
        return s[0]+'_'+s[1]
    return "{}_\\{}{{{}}}".format(s[0], ESCAPE_SEQ, s[1:])

inline_matchers = [re.compile(r) for r in inline_regex]
replacements=set()
for matc in inline_matchers:
    for m in matc.finditer(raw_text):
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
        replacements.add((detected, formatted))

for _from, _to in replacements:
    raw_text = raw_text.replace(_from, _to)

#print(results)

# Step X: patch unicode characters to latex
for k in unimap:
    raw_text = raw_text.replace(k, unimap[k] + ' ')

print(raw_text)
# %%
