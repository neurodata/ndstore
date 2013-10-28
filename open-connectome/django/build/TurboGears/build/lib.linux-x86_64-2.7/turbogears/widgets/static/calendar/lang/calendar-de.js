// Calendar i18n
// Language: de (German)
// Encoding: any
// Author: Jack (tR), <jack@jtr.de>
// Distributed under the same terms as the calendar itself.

// full day names
Calendar._DN = new Array
("Sonntag",
 "Montag",
 "Dienstag",
 "Mittwoch",
 "Donnerstag",
 "Freitag",
 "Samstag",
 "Sonntag");

// short day names
Calendar._SDN = new Array
("So",
 "Mo",
 "Di",
 "Mi",
 "Do",
 "Fr",
 "Sa",
 "So");

// First day of the week. "0" means display Sunday first.
Calendar._FD = 0;

// full month names
Calendar._MN = new Array
("Januar",
 "Februar",
 "M\xe4rz",
 "April",
 "Mai",
 "Juni",
 "Juli",
 "August",
 "September",
 "Oktober",
 "November",
 "Dezember");

// short month names
Calendar._SMN = new Array
("Jan",
 "Feb",
 "M\xe4r",
 "Apr",
 "Mai",
 "Jun",
 "Jul",
 "Aug",
 "Sep",
 "Okt",
 "Nov",
 "Dez");

// tooltips
Calendar._TT = {};
Calendar._TT["INFO"] = "\xDCber dieses Kalendermodul";

Calendar._TT["ABOUT"] =
"DHTML Date/Time Selector\n" +
"(c) dynarch.com 2002-2005 / Author: Mihai Bazon\n" + // don't translate this ;-)
"For latest version visit: http://www.dynarch.com/projects/calendar/\n" +
"Distributed under GNU LGPL.  See http://gnu.org/licenses/lgpl.html for details." +
"\n\n" +
"Datum ausw\xe4hlen:\n" +
"- Benutzen Sie die Kn\xf6pfe \xab und \xbb, um das Jahr auszuw\xe4hlen.\n" +
"- Benutzen Sie die Kn\xf6pfe \u2039 und \u203a, um den Monat auszuw\xe4hlen.\n" +
"- Zur Schnellauswahl halten Sie die Maustaste \xfcber diesen Kn\xf6pfen gedr\xfcckt.";
Calendar._TT["ABOUT_TIME"] = "\n\n" +
"Zeit ausw\xe4hlen:\n" +
"- Klicken Sie auf die Teile der Uhrzeit, um diese zu erh\xF6hen,\n" +
"- oder klicken Sie mit festgehaltener Umschalttaste, um diese zu verringern,\n" +
"- oder klicken und gedr\xfcckt halten zur Schnellauswahl.";

Calendar._TT["TOGGLE"] = "Ersten Tag der Woche w\xe4hlen";
Calendar._TT["PREV_YEAR"] = "Voriges Jahr (Auswahl: l\xe4nger klicken)";
Calendar._TT["PREV_MONTH"] = "Voriger Monat (Auswahl: l\xe4nger klicken)";
Calendar._TT["GO_TODAY"] = "Heute ausw\xe4hlen";
Calendar._TT["NEXT_MONTH"] = "N\xe4chster Monat (Auswahl: l\xe4nger klicken)";
Calendar._TT["NEXT_YEAR"] = "N\xe4chstes Jahr (Auswahl: l\xe4nger klicken)";
Calendar._TT["SEL_DATE"] = "Datum ausw\xe4hlen";
Calendar._TT["DRAG_TO_MOVE"] = "Zum Bewegen gedr\xfcckt halten";
Calendar._TT["PART_TODAY"] = " (Heute)";

// the following is to inform that "%s" is to be the first day of week
// %s will be replaced with the day name.
Calendar._TT["DAY_FIRST"] = "Woche beginnt mit %s";

// This may be locale-dependent.  It specifies the week-end days, as an array
// of comma-separated numbers.  The numbers are from 0 to 6: 0 means Sunday, 1
// means Monday, etc.
Calendar._TT["WEEKEND"] = "0,6";

Calendar._TT["CLOSE"] = "Schlie\xdfen";
Calendar._TT["TODAY"] = "Heute";
Calendar._TT["TIME_PART"] = "(Umschalt-)Klick oder Festhalten und Ziehen, um den Wert zu \xe4ndern";

// date formats
Calendar._TT["DEF_DATE_FORMAT"] = "%d.%m.%Y";
Calendar._TT["TT_DATE_FORMAT"] = "%a, %e. %b";

Calendar._TT["WK"] = "KW";
Calendar._TT["TIME"] = "Uhrzeit:";
