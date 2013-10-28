// Calendar i18n
// Language: uk (Ukrainian)
// Encoding: сp1251
// Author: Сhristoph Zwerschke <cito@online.de>
// Distributed under the same terms as the calendar itself.

// full day names
Calendar._DN = new Array
("Неділя",
 "Понеділок",
 "Вівторок",
 "Середа",
 "Четвер",
 "П'ятниця",
 "Субота",
 "Неділя");

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
("Січень",
 "Лютий",
 "Березень",
 "Квітень",
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
("Січ",
 "Лют",
 "Бер",
 "Кві",
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
"Вибір дати:\n" +
"- Виберіть рік за допомогою кнопок ‹ та ›.\n" +
"- Виберіть місяць за допомогою кнопок « та ».\n" +
"- Для меню швидкого вибору тримайте кнопку нажатою.";
Calendar._TT["ABOUT_TIME"] = "\n\n" +
"Вибір часу:\n" +
"- При кліку на години чи хвилини вони збільшуються.\n" +
"- При кліку з нажатою клавішою Shift вони зменшуються.\n" +
"- Якщо нажати мишку і ворухати нею вправо чи вліво, вони будуть змінюватися скоріше.";

Calendar._TT["PREV_YEAR"] = "На рік назад (тримати нажатою на меню)";
Calendar._TT["PREV_MONTH"] = "На місяць назад (тримати нажатою на меню)";
Calendar._TT["GO_TODAY"] = "Сьогодні";
Calendar._TT["NEXT_MONTH"] = "На місяць вперед (тримати нажатою на меню)";
Calendar._TT["NEXT_YEAR"] = "На рік вперед (тримати нажатою на меню)";
Calendar._TT["SEL_DATE"] = "Вибір дати";
Calendar._TT["DRAG_TO_MOVE"] = "Переніс мишкою";
Calendar._TT["PART_TODAY"] = " (сьогодні)";

// the following is to inform that "%s" is to be the first day of week
// %s will be replaced with the day name.
Calendar._TT["DAY_FIRST"] = "Перший день тижня буде %s";

// This may be locale-dependent.  It specifies the week-end days, as an array
// of comma-separated numbers.  The numbers are from 0 to 6: 0 means Sunday, 1
// means Monday, etc.
Calendar._TT["WEEKEND"] = "0,6";

Calendar._TT["CLOSE"] = "Закрити";
Calendar._TT["TODAY"] = "Сьогодні";
Calendar._TT["TIME_PART"] = "(Shift-)клік чи нажати і ворухати";

// date formats
Calendar._TT["DEF_DATE_FORMAT"] = "%Y-%m-%d";
Calendar._TT["TT_DATE_FORMAT"] = "%e %b, %a";

Calendar._TT["WK"] = "тиж";
Calendar._TT["TIME"] = "Час:";
