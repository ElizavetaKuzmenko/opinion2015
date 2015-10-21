#encoding "utf-8"
#GRAMMAR_ROOT S

ProperName -> Word<h-reg1>+;
Organization -> Adj<gnc-agr[1]>* Noun<gnc-agr[1]>* Word<quoted,gnc-agr[1]>;
Organization -> Adj<gnc-agr[1]>* Noun<gnc-agr[1]>* Word<lat>+;
Author -> Organization | ProperName | Adj<gnc-agr[1]>* Noun<gnc-agr[1],gram="им">;
// Verb_speech -> Verb<kwtype="Speech">;
//S -> Author interp (Author.Name) AnyWord* "SPEECH";
//S -> "END_SPEECH" AnyWord* Author interp (Author.Name);
S -> Author interp (Author.Name) AnyWord* "^";
S -> Dollar AnyWord* Author interp (Author.Name);
