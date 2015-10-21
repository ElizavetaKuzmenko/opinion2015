#encoding "utf-8"
#GRAMMAR_ROOT S

ProperName -> Word<h-reg1>+;
Pun -> "." | "," | "?" | "!" | ";" | ":" | "–" | "»" | QuoteDbl | QuoteSng | LBracket | RBracket| Hyphen;
AdjP -> Adv* Adj<rt>;
PP -> Prep NP;
AuthorGr -> PP | NP;
Organization -> Adj<gnc-agr[1]>* Noun<gnc-agr[1]>* Word<quoted,gnc-agr[1]>;
Organization -> Adj<gnc-agr[1]>* Noun<gnc-agr[1]>* Word<lat>+;
//VP -> Adv* Verb<rt> NP<gram="~nom">*;
VP -> Adv* Verb<rt> PP* NP<gram="~nom">*;
Head -> Noun | ProperName;
NP -> AdjP<gnc-agr[1]>* Head<gnc-agr[1]> AuthorGr*;
Author -> NP;
// Verb_speech -> Verb<kwtype="Speech">;
//S -> Author interp (Author.Name) AnyWord* "SPEECH";
//S -> "END_SPEECH" AnyWord* Author interp (Author.Name);
//S -> Author interp (Author.Name) VP* "^";
//S -> Dollar VP* Author interp (Author.Name);
S -> "~" Pun* VP NP interp (Author.Name);
//RandomWord -> Word | Word Word;
S -> NP interp (Author.Name) VP Pun* (Word) "^";
//S -> NP;
//S -> "~";
//S -> VP NP;

//S -> Pun+;
