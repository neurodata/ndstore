// Calendar i18n
// Language: lv (Latvian)
// Encoding: cp1252
// Author: Juris Valdovskis, <juris@dc.lv>
// Distributed under the same terms as the calendar itself.

// full day names
Calendar._DN = new Array
("Svçtdiena",
 "Pirmdiena",
 "Otrdiena",
 "Treðdiena",
 "Ceturdiena",
 "Piektdiena",
 "Sestdiena",
 "Svçtdiena");

// short day names
Calendar._SDN = new Array
("Sv",
 "Pr",
 "Ot",
 "Tr",
 "Ce",
 "Pk",
 "Se",
 "Sv");

// First day of the week. "0" means display Sunday first.
Calendar._FD = 0;

// full month names
Calendar._MN = new Array
("Janvâris",
 "Februâris",
 "Marts",
 "Aprîlis",
 "Maijs",
 "Jûnijs",
 "Jûlijs",
 "Augusts",
 "Septembris",
 "Oktobris",
 "Novembris",
 "Decembris");

// short month names
Calendar._SMN = new Array
("Jan",
 "Feb",
 "Mar",
 "Apr",
 "Mai",
 "Jûn",
 "Jûl",
 "Aug",
 "Sep",
 "Okt",
 "Nov",
 "Dec");

// tooltips
Calendar._TT = {};
Calendar._TT["INFO"] = "Par kalendâru";

Calendar._TT["ABOUT"] =
"DHTML Date/Time Selector\n" +
"(c) dynarch.com 2002-2005 / Author: Mihai Bazon\n" + // don't translate this this ;-)
"For latest version visit: http://www.dynarch.com/projects/calendar/\n" +
"Distributed under GNU LGPL.  See http://gnu.org/licenses/lgpl.html for details." +
"\n\n" +
"Datuma izvçle:\n" +
"- Izmanto \xab, \xbb pogas, lai izvçlçtos gadu\n" +
"- Izmanto " + String.fromCharCode(0x2039) + ", " + String.fromCharCode(0x203a) + "pogas, lai izvçlçtos mçnesi\n" +
"- Turi nospiestu peles pogu uz jebkuru no augstâk minçtajâm pogâm, lai paâtrinâtu izvçli.";
Calendar._TT["ABOUT_TIME"] = "\n\n" +
"Laika izvçle:\n" +
"- Uzklikðíini uz jebkuru no laika daïâm, lai palielinâtu to\n" +
"- vai Shift-klikðíis, lai samazinâtu to\n" +
"- vai noklikðíini un velc uz attiecîgo virzienu lai mainîtu âtrâk.";

Calendar._TT["PREV_YEAR"] = "Iepr. gads (turi izvçlnei)";
Calendar._TT["PREV_MONTH"] = "Iepr. mçnesis (turi izvçlnei)";
Calendar._TT["GO_TODAY"] = "Ðodien";
Calendar._TT["NEXT_MONTH"] = "Nâkoðais mçnesis (turi izvçlnei)";
Calendar._TT["NEXT_YEAR"] = "Nâkoðais gads (turi izvçlnei)";
Calendar._TT["SEL_DATE"] = "Izvçlies datumu";
Calendar._TT["DRAG_TO_MOVE"] = "Velc, lai pârvietotu";
Calendar._TT["PART_TODAY"] = " (ðodien)";

// the following is to inform that "%s" is to be the first day of week
// %s will be replaced with the day name.
Calendar._TT["DAY_FIRST"] = "Attçlot %s kâ pirmo";

// This may be locale-dependent.  It specifies the week-end days, as an array
// of comma-separated numbers.  The numbers are from 0 to 6: 0 means Sunday, 1
// means Monday, etc.
Calendar._TT["WEEKEND"] = "1,7";

Calendar._TT["CLOSE"] = "Aizvçrt";
Calendar._TT["TODAY"] = "Ðodien";
Calendar._TT["TIME_PART"] = "(Shift-)Klikðíis vai pârvieto, lai mainîtu";

// date formats
Calendar._TT["DEF_DATE_FORMAT"] = "%d-%m-%Y";
Calendar._TT["TT_DATE_FORMAT"] = "%a, %e %b";

Calendar._TT["WK"] = "wk";
Calendar._TT["TIME"] = "Laiks:";
