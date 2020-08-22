80 CHAPTER 1 / REGULAR LANGUAGES To use the pumping lemma to prove that a language B is not regular, first as- sume that B is regular in order to obtain a contradiction. Then use the pumping lemma to guarantee the existence of a pumping length p such that all strings of length p or greater in B can be pumped. Next, find a string s in B that has length p or greater but that cannot be pumped. Finally, demonstrate that s cannot be pumped by considering all ways of dividing s into x, y, and z (taking condition 3 of the pumping lemma into account if convenient) and, for each such division, finding a value i where xyi z $6\in  B$. This final step often involves grouping the various ways of dividing s into several cases and analyzing them individually.

The existence of s contradicts the pumping lemma if B were regular. Hence B cannot be regular.

Finding s sometimes takes a bit of creative thinking. You may need to hunt through several candidates for s before you discover one that works. Try mem- bers of B that seem to exhibit the “essence” of B’s nonregularity. We further discuss the task of finding s in some of the following examples.

EXAMPLE 1.73 Let B be the language {0n 1n |n \ge 0}. We use the pumping lemma to prove that B is not regular. The proof is by contradiction.

Assume to the contrary that B is regular. Let p be the pumping length given by the pumping lemma. Choose s to be the string 0p 1p . Because s is a member of B and s has length more than p, the pumping lemma guarantees that s can be split into three pieces, $s = xyz$, where for any i \ge 0 the string xyi z is in B. We consider three cases to show that this result is impossible.

1. The string y consists only of 0s. In this case, the string xyyz has more 0s than 1s and so is not a member of B, violating condition 1 of the pumping lemma. This case is a contradiction.
1. The string y consists only of 1s. This case also gives a contradiction.
1. The string y consists of both 0s and 1s. In this case, the string xyyz may have the same number of 0s and 1s, but they will be out of order with some 1s before 0s. Hence it is not a member of B, which is a contradiction.

Thus a contradiction is unavoidable if we make the assumption that B is reg- ular, so B is not regular. Note that we can simplify this argument by applying condition 3 of the pumping lemma to eliminate cases 2 and 3.

In this example, finding the string s was easy because any string in B of length p or more would work. In the next two examples, some choices for s do not work so additional care is required.

EXAMPLE 1.74 Let $C = \{w| w has an eq_\mathrm{ual} number of 0s and 1s\}$. We use the pumping lemma to prove that C is not regular. The proof is by contradiction.

Copyright 2012 Cengage Learning. All Rights Reserved. May not be copied, scanned, or duplicated, in whole or in part. Due to electronic rights, some third party content may be suppressed from the eBook and/or eChapter(s). Editorial review has deemed that any suppressed content does not materially affect the overall learning experience. Cengage Learning reserves the right to remove additional content at any time if subsequent rights restrictions require it.

3.1 TURING MACHINES 173 EXAMPLE 3.9 The following is a formal description of $M1 = (Q, \Sigma , \Gamma , \delta , q_1, q_\mathrm{accept}, q_\mathrm{reject})$, the Turing machine that we informally described (page 167) for deciding the lan- guage $B = \{w\#w| w \in  \{0,1\}$∗ }.

- $Q = \{q_1, ... , q_8, q_\mathrm{accept}, q_\mathrm{reject}\}$,
- $\Sigma  = \{0,1,\#\}$, and $\Gamma  = \{0,1,\#,x, \}$.
- We describe \delta with a state diagram (see the following figure).
- The start, accept, and reject states are q1, qaccept, and qreject, respectively.

FIGURE 3.10 State diagram for Turing machine M1 In Figure 3.10, which depicts the state diagram of TM M1, you will find the label 0,1\rightarrowR on the transition going from q3 to itself. That label means that the machine stays in q3 and moves to the right when it reads a 0 or a 1 in state q3. It doesn’t change the symbol on the tape.

Stage 1 is implemented by states q1 through q7, and stage 2 by the remaining states. To simplify the figure, we don’t show the reject state or the transitions going to the reject state. Those transitions occur implicitly whenever a state lacks an outgoing transition for a particular symbol. Thus because in state q5 no outgoing arrow with a # is present, if a # occurs under the head when the machine is in state q5, it goes to state qreject. For completeness, we say that the head moves right in each of these transitions to the reject state.

Copyright 2012 Cengage Learning. All Rights Reserved. May not be copied, scanned, or duplicated, in whole or in part. Due to electronic rights, some third party content may be suppressed from the eBook and/or eChapter(s). Editorial review has deemed that any suppressed content does not materially affect the overall learning experience. Cengage Learning reserves the right to remove additional content at any time if subsequent rights restrictions require it.

1. test test
1. test test test
1. test 3.1 EXAMPLE TURING MACHINES 173 3.9 The following is a formal description of $M1 = (Q, \Sigma , \Gamma , \delta , q_1 , q_\mathrm{accept} , q_\mathrm{reject} )$, the Turing machine that we informally described (page 167) for deciding the language $B = \{w\#w| w \in  \{0,1\}$∗ }.

- $Q = \{q_1 , ... , q_8 , q_\mathrm{accept} , q_\mathrm{reject} \}$, • $\Sigma  = \{0,1,\#\}$, and $\Gamma  = \{0,1,\#,x, \}$.
- We describe \delta with a state diagram (see the following figure).
- The start, accept, and reject states are q1 , qaccept , and qreject , respectively.

FIGURE 3.10 State diagram for Turing machine M1 In Figure 3.10, which depicts the state diagram of TM M1 , you will find the label 0,1\rightarrowR on the transition going from q3 to itself. That label means that the machine stays in q3 and moves to the right when it reads a 0 or a 1 in state q3 . It doesn’t change the symbol on the tape.

Stage 1 is implemented by states q1 through q7 , and stage 2 by the remaining states. To simplify the figure, we don’t show the reject state or the transitions going to the reject state. Those transitions occur implicitly whenever a state lacks an outgoing transition for a particular symbol. Thus because in state q5 no outgoing arrow with a # is present, if a # occurs under the head when the machine is in state q5 , it goes to state qreject . For completeness, we say that the head moves right in each of these transitions to the reject state.

Copyright 2012 Cengage Learning. All Rights Reserved. May not be copied, scanned, or duplicated, in whole or in part. Due to electronic rights, some third party content may be suppressed from the eBook and/or eChapter(s). Editorial review has deemed that any suppressed content does not materially affect the overall learning experience. Cengage Learning reserves the right to remove additional content at any time if subsequent rights restrictions require it.

