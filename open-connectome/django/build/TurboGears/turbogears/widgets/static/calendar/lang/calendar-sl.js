// Calendar i18n
// Language: sl (Slovenian)
// Encoding: any
// Author: David Milost <mercy@volja.net>
// Distributed under the same terms as the calendar itself.

 // full day names
Calendar._DN = new Array
("Nedelja",
 "Ponedeljek",
 "Torek",
 "Sreda",
 "\u010cetrtek",
 "Petek",
 "Sobota",
 "Nedelja");
 // short day names
 Calendar._SDN = new Array
("Ned",
 "Pon",
 "Tor",
 "Sre",
 "\u010cet",
 "Pet",
 "Sob",
 "Ned");
 // First day of the week. "0" means display Sunday first.
Calendar._FD = 0;
// short month names
Calendar._SMN = new Array
("Jan",
 "Feb",
 "Mar",
 "Apr",
 "Maj",
 "Jun",
 "Jul",
 "Avg",
 "Sep",
 "Okt",
 "Nov",
 "Dec");
  // full month names
Calendar._MN = new Array
("Januar",
 "Februar",
 "Marec",
 "April",
 "Maj",
 "Junij",
 "Julij",
 "Avgust",
 "September",
 "Oktober",
 "November",
 "December");

// tooltips
// tooltips
Calendar._TT = {};
Calendar._TT["INFO"] = "O koledarju";

Calendar._TT["ABOUT"] =
"DHTML Date/Time Selector\n" +
"(c) dynarch.com 2002-2005 / Author: Mihai Bazon\n" + // don't translate this this ;-)
"Za zadnjo verzijo pojdine na naslov: http://www.dynarch.com/projects/calendar/\n" +
"Distribuirano pod GNU LGPL.  Poglejte http://gnu.org/licenses/lgpl.html za podrobnosti." +
"\n\n" +
"Izbor datuma:\n" +
"- Uporabite \xab, \xbb gumbe za izbor leta\n" +
"- Uporabite " + String.fromCharCode(0x2039) + ", " + String.fromCharCode(0x203a) + " gumbe za izbor meseca\n" +
"- Zadr\u017eite klik na kateremkoli od zgornjih gumbov za hiter izbor.";
Calendar._TT["ABOUT_TIME"] = "\n\n" +
"Izbor \u0107asa:\n" +
"- Kliknite na katerikoli del \u0107asa za pove\u0107. le-tega\n" +
"- ali Shift-click za zmanj. le-tega\n" +
"- ali kliknite in povlecite za hiter izbor.";

Calendar._TT["PREV_YEAR"] = "Predhodnje leto (dolg klik za meni)";
Calendar._TT["PREV_MONTH"] = "Predhodnji mesec (dolg klik za meni)";
Calendar._TT["GO_TODAY"] = "Pojdi na teko\u0107i dan";
Calendar._TT["NEXT_MONTH"] = "Naslednji mesec (dolg klik za meni)";
Calendar._TT["NEXT_YEAR"] = "Naslednje leto (dolg klik za meni)";
Calendar._TT["SEL_DATE"] = "Izberite datum";
Calendar._TT["DRAG_TO_MOVE"] = "Pritisni in povleci za spremembo pozicije";
Calendar._TT["PART_TODAY"] = " (danes)";
Calendar._TT["DAY_FIRST"] = "Prika\u017ei %s kot prvi dan";
Calendar._TT["WEEKEND"] = "0,6";
Calendar._TT["CLOSE"] = "Zapri";
Calendar._TT["TODAY"] = "Danes";

// date formats
Calendar._TT["DEF_DATE_FORMAT"] = "%Y-%m-%d";
Calendar._TT["TT_DATE_FORMAT"] = "%a, %b %e";

Calendar._TT["WK"] = "Ted";
Calendar._TT["TIME"] = "\u0106as:";
