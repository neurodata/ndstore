// Calendar i18n
// Language: ca (Catalan)
// Encoding: any
// Author: Mihai Bazon, <mihai_bazon@yahoo.com>
// Distributed under the same terms as the calendar itself.

// full day names
Calendar._DN = new Array
("Diumenge",
 "Dilluns",
 "Dimarts",
 "Dimecres",
 "Dijous",
 "Divendres",
 "Dissabte",
 "Diumenge");

// short day names
Calendar._SDN = new Array
("Diu",
 "Dil",
 "Dmt",
 "Dmc",
 "Dij",
 "Div",
 "Dis",
 "Diu");

// First day of the week. "0" means display Sunday first.
Calendar._FD = 0;

// full month names
Calendar._MN = new Array
("Gener",
 "Febrer",
 "Mar\xe7",
 "Abril",
 "Maig",
 "Juny",
 "Juliol",
 "Agost",
 "Setembre",
 "Octubre",
 "Novembre",
 "Desembre");

// short month names
Calendar._SMN = new Array
("Gen",
 "Feb",
 "Mar",
 "Abr",
 "Mai",
 "Jun",
 "Jul",
 "Ago",
 "Set",
 "Oct",
 "Nov",
 "Des");

// tooltips
Calendar._TT = {};
Calendar._TT["INFO"] = "Sobre el calendari";

Calendar._TT["ABOUT"] =
"DHTML Selector de Data/Hora\n" +
"(c) dynarch.com 2002-2005 / Author: Mihai Bazon\n" + // don't translate this this ;-)
"For latest version visit: http://www.dynarch.com/projects/calendar/\n" +
"Distributed under GNU LGPL.  See http://gnu.org/licenses/lgpl.html for details." +
"\n\n" +
"Sel.lecci\xf3 de Dates:\n" +
"- Fes servir els botons \xab, \xbb per sel.leccionar l'any\n" +
"- Fes servir els botons " + String.fromCharCode(0x2039) + ", " + String.fromCharCode(0x203a) + " per se.lecciconar el mes\n" +
"- Mant\xe9 el ratol\xed apretat en qualsevol dels anteriors per sel.lecci\xf3 r\xe0pida.";
Calendar._TT["ABOUT_TIME"] = "\n\n" +
"Time selection:\n" +
"- claca en qualsevol de les parts de la hora per augmentar-les\n" +
"- o Shift-click per decrementar-la\n" +
"- or click and arrastra per sel.lecci\xf3 r\xe0pida.";

Calendar._TT["PREV_YEAR"] = "Any anterior (Mantenir per menu)";
Calendar._TT["PREV_MONTH"] = "Mes anterior (Mantenir per menu)";
Calendar._TT["GO_TODAY"] = "Anar a avui";
Calendar._TT["NEXT_MONTH"] = "Mes seg\xfcent (Mantenir per menu)";
Calendar._TT["NEXT_YEAR"] = "Any seg\xfcent (Mantenir per menu)";
Calendar._TT["SEL_DATE"] = "Sel.leccionar data";
Calendar._TT["DRAG_TO_MOVE"] = "Arrastrar per moure";
Calendar._TT["PART_TODAY"] = " (avui)";

// the following is to inform that "%s" is to be the first day of week
// %s will be replaced with the day name.
Calendar._TT["DAY_FIRST"] = "Mostra %s primer";

// This may be locale-dependent.  It specifies the week-end days, as an array
// of comma-separated numbers.  The numbers are from 0 to 6: 0 means Sunday, 1
// means Monday, etc.
Calendar._TT["WEEKEND"] = "0,6";

Calendar._TT["CLOSE"] = "Tanca";
Calendar._TT["TODAY"] = "Avui";
Calendar._TT["TIME_PART"] = "(Shift-)Click a arrastra per canviar el valor";

// date formats
Calendar._TT["DEF_DATE_FORMAT"] = "%Y-%m-%d";
Calendar._TT["TT_DATE_FORMAT"] = "%a, %b %e";

Calendar._TT["WK"] = "st";
Calendar._TT["TIME"] = "Hora:";
