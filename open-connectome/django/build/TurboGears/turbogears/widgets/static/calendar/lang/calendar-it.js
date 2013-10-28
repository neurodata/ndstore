// Calendar i18n
// Language: it (Italian)
// Encoding: utf-8
// Author: Fabio Di Bernardini, <altraqua@email.it>
// Distributed under the same terms as the calendar itself.

// full day names
Calendar._DN = new Array
("Domenica",
 "Lunedì",
 "Martedì",
 "Mercoledì",
 "Giovedì",
 "Venerdì",
 "Sabato",
 "Domenica");

// short day names
Calendar._SDN = new Array
("Dom",
 "Lun",
 "Mar",
 "Mer",
 "Gio",
 "Ven",
 "Sab",
 "Dom");

// First day of the week. "0" means display Sunday first.
Calendar._FD = 0;

// full month names
Calendar._MN = new Array
("Gennaio",
 "Febbraio",
 "Marzo",
 "Aprile",
 "Maggio",
 "Giugno",
 "Luglio",
 "Agosto",
 "Settembre",
 "Ottobre",
 "Novembre",
 "Dicembre");

// short month names
Calendar._SMN = new Array
("Gen",
 "Feb",
 "Mar",
 "Apr",
 "Mag",
 "Giu",
 "Lug",
 "Ago",
 "Set",
 "Ott",
 "Nov",
 "Dic");

// tooltips
Calendar._TT = {};
Calendar._TT["INFO"] = "Informazioni sul calendario";

Calendar._TT["ABOUT"] =
"DHTML Date/Time Selector\n" +
"(c) dynarch.com 2002-2005 / Author: Mihai Bazon\n" + // don't translate this this ;-)
"Per gli aggiornamenti: http://www.dynarch.com/projects/calendar/\n" +
"Distribuito sotto licenza GNU LGPL.  Vedi http://gnu.org/licenses/lgpl.html per i dettagli." +
"\n\n" +
"Selezione data:\n" +
"- Usa \xab, \xbb per selezionare l'anno\n" +
"- Usa  " + String.fromCharCode(0x2039) + ", " + String.fromCharCode(0x203a) + " per i mesi\n" +
"- Tieni premuto a lungo il mouse per accedere alle funzioni di selezione veloce.";
Calendar._TT["ABOUT_TIME"] = "\n\n" +
"Selezione orario:\n" +
"- Clicca sul numero per incrementarlo\n" +
"- o Shift+click per decrementarlo\n" +
"- o click e sinistra o destra per variarlo.";

Calendar._TT["PREV_YEAR"] = "Anno prec.(clicca a lungo per il menù)";
Calendar._TT["PREV_MONTH"] = "Mese prec. (clicca a lungo per il menù)";
Calendar._TT["GO_TODAY"] = "Oggi";
Calendar._TT["NEXT_MONTH"] = "Pross. mese (clicca a lungo per il menù)";
Calendar._TT["NEXT_YEAR"] = "Pross. anno (clicca a lungo per il menù)";
Calendar._TT["SEL_DATE"] = "Seleziona data";
Calendar._TT["DRAG_TO_MOVE"] = "Trascina per spostarlo";
Calendar._TT["PART_TODAY"] = " (oggi)";

// the following is to inform that "%s" is to be the first day of week
// %s will be replaced with the day name.
Calendar._TT["DAY_FIRST"] = "Mostra prima %s";

// This may be locale-dependent.  It specifies the week-end days, as an array
// of comma-separated numbers.  The numbers are from 0 to 6: 0 means Sunday, 1
// means Monday, etc.
Calendar._TT["WEEKEND"] = "0,6";

Calendar._TT["CLOSE"] = "Chiudi";
Calendar._TT["TODAY"] = "Oggi";
Calendar._TT["TIME_PART"] = "(Shift-)Click o trascina per cambiare il valore";

// date formats
Calendar._TT["DEF_DATE_FORMAT"] = "%d-%m-%Y";
Calendar._TT["TT_DATE_FORMAT"] = "%a:%b:%e";

Calendar._TT["WK"] = "set";
Calendar._TT["TIME"] = "Ora:";
