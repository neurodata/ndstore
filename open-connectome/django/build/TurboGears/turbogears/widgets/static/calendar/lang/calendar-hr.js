// Calendar i18n
// Language: hr (Croatian)
// Encoding: utf-8
// Author: Krunoslav Zubrinic <krunoslav.zubrinic@vip.hr>, Dejan Rodiger <dejan.rodiger@ck.t-com.hr>
// Distributed under the same terms as the calendar itself.

// full day names
Calendar._DN = new Array
("Nedjelja",
 "Ponedjeljak",
 "Utorak",
 "Srijeda",
 "Četvrtak",
 "Petak",
 "Subota",
 "Nedjelja");

// short day names
Calendar._SDN = new Array
("Ned",
 "Pon",
 "Uto",
 "Sri",
 "Čet",
 "Pet",
 "Sub",
 "Ned");

// First day of the week. "0" means display Sunday first, "1" means display
// Monday first, etc.
Calendar._FD = 1;

Calendar._MN = new Array
("Siječanj",
 "Veljača",
 "Ožujak",
 "Travanj",
 "Svibanj",
 "Lipanj",
 "Srpanj",
 "Kolovoz",
 "Rujan",
 "Listopad",
 "Studeni",
 "Prosinac");

Calendar._SMN = new Array
("Sij",
 "Vel",
 "Ožu",
 "Tra",
 "Svi",
 "Lip",
 "Srp",
 "Kol",
 "Ruj",
 "Lis",
 "Stu",
 "Pro");

// tooltips
Calendar._TT = {};
Calendar._TT["TOGGLE"] = "Promjeni dan s kojim počinje tjedan";
Calendar._TT["PREV_YEAR"] = "Prethodna godina (dugi pritisak za meni)";
Calendar._TT["PREV_MONTH"] = "Prethodni mjesec (dugi pritisak za meni)";
Calendar._TT["GO_TODAY"] = "Idi na tekući dan";
Calendar._TT["NEXT_MONTH"] = "Slijedeći mjesec (dugi pritisak za meni)";
Calendar._TT["NEXT_YEAR"] = "Slijedeća godina (dugi pritisak za meni)";
Calendar._TT["SEL_DATE"] = "Izaberite datum";
Calendar._TT["DRAG_TO_MOVE"] = "Pritisni i povuci za promjenu pozicije";
Calendar._TT["PART_TODAY"] = " (today)";
Calendar._TT["MON_FIRST"] = "Postavi ponedjeljak kao prvi dan";
Calendar._TT["SUN_FIRST"] = "Postavi nedjelju kao prvi dan";
Calendar._TT["CLOSE"] = "Zatvori";
Calendar._TT["TODAY"] = "Danas";

// Added by Dejan Rodiger <dejan.rodiger@ck.t-com.hr>
Calendar._TT["INFO"] = "O kalendaru";
Calendar._TT["ABOUT"] =
"DHTML Date/Time Izbornik\n" +
"(c) dynarch.com 2002-2005 / Autor: Mihai Bazon\n" + // don't translate this this ;-)
"Za zadnju verziju posjetite: http://www.dynarch.com/projects/calendar/\n" +
"Distribuirano pod GNU LGPL.  Vidite http://gnu.org/licenses/lgpl.html za detalje oko licence." +
"\n\n" +
"Odabir datuma:\n" +
"- Koristite gumbe \xab, \xbb za odabir godine\n" +
"- Koristite gumbe " + String.fromCharCode(0x2039) + ", " + String.fromCharCode(0x203a) + " za odabir mjeseca\n" +
"- Kliknite mišem na bilo koju tpiku za brzi odabir.";
Calendar._TT["ABOUT_TIME"] = "\n\n" +
"Odabir vremena:\n" +
"- Kliknite na bilo koji dio vremena da bi ga povečali\n" +
"- ili Shift-klik da bi ga smanjili\n" +
"- ili kliknite i povucite za brži odabir.";
Calendar._TT["WEEKEND"] = "0,6";
Calendar._TT["TIME"] = "Vrijeme:";
Calendar._TT["DAY_FIRST"] = "Postavi %s kao prvi dan";
Calendar._TT["TIME_PART"] = "(Shift-)klik ili kliknite i vucite da primijenite vrijednost";

// date formats
Calendar._TT["DEF_DATE_FORMAT"] = "%d.%m.%y";
Calendar._TT["TT_DATE_FORMAT"] = "%a, %b %e";

Calendar._TT["WK"] = "Tje";
