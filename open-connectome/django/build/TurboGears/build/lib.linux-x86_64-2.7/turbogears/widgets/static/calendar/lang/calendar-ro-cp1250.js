// Calendar i18n
// Language: ro (Romanian)
// Encoding: cp1250
// Author: Mihai Bazon, <mihai_bazon@yahoo.com>
// Distributed under the same terms as the calendar itself.

Calendar._DN = new Array
("Duminicã",
 "Luni",
 "Marþi",
 "Miercuri",
 "Joi",
 "Vineri",
 "Sâmbãtã",
 "Duminicã");

Calendar._SDN_len = 2;

Calendar._FD = 0;

Calendar._MN = new Array
("Ianuarie",
 "Februarie",
 "Martie",
 "Aprilie",
 "Mai",
 "Iunie",
 "Iulie",
 "August",
 "Septembrie",
 "Octombrie",
 "Noiembrie",
 "Decembrie");

// tooltips
Calendar._TT = {};

Calendar._TT["INFO"] = "Despre calendar";

Calendar._TT["ABOUT"] =
"DHTML Date/Time Selector\n" +
"(c) dynarch.com 2002-2005 / Author: Mihai Bazon\n" + // don't translate this this ;-)
"Pentru ultima versiune vizitaþi: http://www.dynarch.com/projects/calendar/\n" +
"Distribuit sub GNU LGPL.  See http://gnu.org/licenses/lgpl.html for details." +
"\n\n" +
"Selecþia datei:\n" +
"- Folosiþi butoanele \xab, \xbb pentru a selecta anul\n" +
"- Folosiþi butoanele " + String.fromCharCode(0x2039) + ", " + String.fromCharCode(0x203a) + " pentru a selecta luna\n" +
"- Tineþi butonul mouse-ului apãsat pentru selecþie mai rapidã.";
Calendar._TT["ABOUT_TIME"] = "\n\n" +
"Selecþia orei:\n" +
"- Click pe ora sau minut pentru a mãri valoarea cu 1\n" +
"- Sau Shift-Click pentru a micºora valoarea cu 1\n" +
"- Sau Click ºi drag pentru a selecta mai repede.";

Calendar._TT["PREV_YEAR"] = "Anul precedent (lung pt menu)";
Calendar._TT["PREV_MONTH"] = "Luna precedentã (lung pt menu)";
Calendar._TT["GO_TODAY"] = "Data de azi";
Calendar._TT["NEXT_MONTH"] = "Luna urmãtoare (lung pt menu)";
Calendar._TT["NEXT_YEAR"] = "Anul urmãtor (lung pt menu)";
Calendar._TT["SEL_DATE"] = "Selecteazã data";
Calendar._TT["DRAG_TO_MOVE"] = "Trage pentru a miºca";
Calendar._TT["PART_TODAY"] = " (astãzi)";
Calendar._TT["DAY_FIRST"] = "Afiºeazã %s prima zi";
Calendar._TT["WEEKEND"] = "0,6";
Calendar._TT["CLOSE"] = "Închide";
Calendar._TT["TODAY"] = "Astãzi";
Calendar._TT["TIME_PART"] = "(Shift-)Click sau drag pentru a selecta";

// date formats
Calendar._TT["DEF_DATE_FORMAT"] = "%d-%m-%Y";
Calendar._TT["TT_DATE_FORMAT"] = "%A, %d %B";

Calendar._TT["WK"] = "spt";
Calendar._TT["TIME"] = "Ora:";
