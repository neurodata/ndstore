// Calendar i18n
// Language: uk (Ukrainian)
// Encoding: koi8-u
// Author: Сhristoph Zwerschke <cito@online.de>
// Distributed under the same terms as the calendar itself.

// full day names
Calendar._DN = new Array
("Нед╕ля",
 "Понед╕лок",
 "В╕второк",
 "Середа",
 "Четвер",
 "П'ятниця",
 "Субота",
 "Нед╕ля");

// short day names
Calendar._SDN = new Array
("Нд",
 "Пн",
 "Вт",
 "Ср",
 "Чт",
 "Пт",
 "Сб",
 "Нд");

// First day of the week. "0" means display Sunday first, "1" means display
// Monday first, etc.
Calendar._FD = 1;

// full month names
Calendar._MN = new Array
("С╕чень",
 "Лютий",
 "Березень",
 "Кв╕тень",
 "Травень",
 "Червень",
 "Липень",
 "Серпень",
 "Вересень",
 "Жовтень",
 "Листопад",
 "Грудень");

// short month names
Calendar._SMN = new Array
("С╕ч",
 "Лют",
 "Бер",
 "Кв╕",
 "Тра",
 "Чер",
 "Лип",
 "Сер",
 "Вер",
 "Жов",
 "Лис",
 "Гру");

// tooltips
Calendar._TT = {};
Calendar._TT["INFO"] = "Про календар...";

Calendar._TT["ABOUT"] =
"DHTML Date/Time Selector\n" +
"(c) dynarch.com 2002-2005 / Author: Mihai Bazon\n" + // don't translate this this ;-)
"For latest version visit: http://www.dynarch.com/projects/calendar/\n" +
"Distributed under GNU LGPL.  See http://gnu.org/licenses/lgpl.html for details." +
"\n\n" +
"Виб╕р дати:\n" +
"- Вибер╕ть р╕к за допомогою кнопок \xab та \xbb.\n" +
"- Вибер╕ть м╕сяць за допомогою кнопок \u2039 та \u203a.\n" +
"- Для меню швидкого вибору тримайте кнопку нажатою.";
Calendar._TT["ABOUT_TIME"] = "\n\n" +
"Виб╕р часу:\n" +
"- При кл╕ку на години чи хвилини вони зб╕льшуються.\n" +
"- При кл╕ку з нажатою клав╕шою Shift вони зменшуються.\n" +
"- Якщо нажати мишку ╕ ворухати нею вправо чи вл╕во, вони будуть зм╕нюватися скор╕ше.";

Calendar._TT["PREV_YEAR"] = "На р╕к назад (тримати нажатою на меню)";
Calendar._TT["PREV_MONTH"] = "На м╕сяць назад (тримати нажатою на меню)";
Calendar._TT["GO_TODAY"] = "Сьогодн╕";
Calendar._TT["NEXT_MONTH"] = "На м╕сяць вперед (тримати нажатою на меню)";
Calendar._TT["NEXT_YEAR"] = "На р╕к вперед (тримати нажатою на меню)";
Calendar._TT["SEL_DATE"] = "Виб╕р дати";
Calendar._TT["DRAG_TO_MOVE"] = "Перен╕с мишкою";
Calendar._TT["PART_TODAY"] = " (сьогодн╕)";

// the following is to inform that "%s" is to be the first day of week
// %s will be replaced with the day name.
Calendar._TT["DAY_FIRST"] = "Перший день тижня буде %s";

// This may be locale-dependent.  It specifies the week-end days, as an array
// of comma-separated numbers.  The numbers are from 0 to 6: 0 means Sunday, 1
// means Monday, etc.
Calendar._TT["WEEKEND"] = "0,6";

Calendar._TT["CLOSE"] = "Закрити";
Calendar._TT["TODAY"] = "Сьогодн╕";
Calendar._TT["TIME_PART"] = "(Shift-)кл╕к чи нажати ╕ ворухати";

// date formats
Calendar._TT["DEF_DATE_FORMAT"] = "%Y-%m-%d";
Calendar._TT["TT_DATE_FORMAT"] = "%e %b, %a";

Calendar._TT["WK"] = "тиж";
Calendar._TT["TIME"] = "Час:";
