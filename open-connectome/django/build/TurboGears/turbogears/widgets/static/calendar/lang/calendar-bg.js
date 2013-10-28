// Calendar i18n
// Language: bg (Bulgarian)
// Encoding: utf-8
// Author: Valentin Sheiretsky, <valio@valio.eu.org>
// Distributed under the same terms as the calendar itself.

// full day names
Calendar._DN = new Array
("Неделя",
 "Понеделник",
 "Вторник",
 "Сряда",
 "Четвъртък",
 "Петък",
 "Събота",
 "Неделя");

// short day names
Calendar._SDN = new Array
("Нед",
 "Пон",
 "Вто",
 "Сря",
 "Чет",
 "Пет",
 "Съб",
 "Нед");

// First day of the week. "0" means display Sunday first.
Calendar._FD = 0;

// full month names
Calendar._MN = new Array
("Януари",
 "Февруари",
 "Март",
 "Април",
 "Май",
 "Юни",
 "Юли",
 "Август",
 "Септември",
 "Октомври",
 "Ноември",
 "Декември");

// short month names
Calendar._SMN = new Array
("Яну",
 "Фев",
 "Мар",
 "Апр",
 "Май",
 "Юни",
 "Юли",
 "Авг",
 "Сеп",
 "Окт",
 "Ное",
 "Дек");

// tooltips
Calendar._TT = {};
Calendar._TT["INFO"] = "Информация за календара";

Calendar._TT["ABOUT"] =
"DHTML Date/Time Selector\n" +
"(c) dynarch.com 2002-2005 / Author: Mihai Bazon\n" + // don't translate this this ;-)
"For latest version visit: http://www.dynarch.com/projects/calendar/\n" +
"Distributed under GNU LGPL.  See http://gnu.org/licenses/lgpl.html for details." +
"\n\n" +
"Date selection:\n" +
"- Use the \xab, \xbb buttons to select year\n" +
"- Use the " + String.fromCharCode(0x2039) + ", " + String.fromCharCode(0x203a) + " buttons to select month\n" +
"- Hold mouse button on any of the above buttons for faster selection.";
Calendar._TT["ABOUT_TIME"] = "\n\n" +
"Time selection:\n" +
"- Click on any of the time parts to increase it\n" +
"- or Shift-click to decrease it\n" +
"- or click and drag for faster selection.";

Calendar._TT["PREV_YEAR"] = "Предна година (задръжте за меню)";
Calendar._TT["PREV_MONTH"] = "Преден месец (задръжте за меню)";
Calendar._TT["GO_TODAY"] = "Изберете днес";
Calendar._TT["NEXT_MONTH"] = "Следващ месец (задръжте за меню)";
Calendar._TT["NEXT_YEAR"] = "Следваща година (задръжте за меню)";
Calendar._TT["SEL_DATE"] = "Изберете дата";
Calendar._TT["DRAG_TO_MOVE"] = "Преместване";
Calendar._TT["PART_TODAY"] = " (днес)";

// the following is to inform that "%s" is to be the first day of week
// %s will be replaced with the day name.
Calendar._TT["DAY_FIRST"] = "%s като първи ден";

// This may be locale-dependent.  It specifies the week-end days, as an array
// of comma-separated numbers.  The numbers are from 0 to 6: 0 means Sunday, 1
// means Monday, etc.
Calendar._TT["WEEKEND"] = "0,6";

Calendar._TT["CLOSE"] = "Затворете";
Calendar._TT["TODAY"] = "Днес";
Calendar._TT["TIME_PART"] = "(Shift-)Click или drag за да промените стойността";

// date formats
Calendar._TT["DEF_DATE_FORMAT"] = "%Y-%m-%d";
Calendar._TT["TT_DATE_FORMAT"] = "%A - %e %B %Y";

Calendar._TT["WK"] = "Седм";
Calendar._TT["TIME"] = "Час:";
