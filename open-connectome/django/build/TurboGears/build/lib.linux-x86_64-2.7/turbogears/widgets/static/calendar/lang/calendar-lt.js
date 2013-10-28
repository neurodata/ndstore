// Calendar i18n
// Language: lt (Lithuanian)
// Encoding: utf-8
// Author: Dalius Dobravolskas <dalius.dobravolskas@gmail.com>
// Distributed under the same terms as the calendar itself.

// full day names
Calendar._DN = new Array
("Sekmadienis",
 "Pirmadienis",
 "Antradienis",
 "Trečiadienis",
 "Ketvirtadienis",
 "Penktadienis",
 "Šeštadienis",
 "Sekmadienis");

// short day names
Calendar._SDN = new Array
("Sk",
 "Pr",
 "An",
 "Tr",
 "Ke",
 "Pn",
 "Še",
 "Sk");

// First day of the week. "0" means display Sunday first, "1" means display
// Monday first, etc.
Calendar._FD = 1;

// full month names
Calendar._MN = new Array
("Sausis",
 "Vasaris",
 "Kovas",
 "Balandis",
 "Gegužė",
 "Birželis",
 "Liepa",
 "Rugpjūtis",
 "Rugsėjis",
 "Spalis",
 "Lapkritis",
 "Gruodis");

// short month names
Calendar._SMN = new Array
("Sau",
 "Vas",
 "Kov",
 "Bal",
 "Geg",
 "Bir",
 "Lie",
 "Rgp",
 "Rus",
 "Spa",
 "Lap",
 "Grd");

// tooltips
Calendar._TT = {};
Calendar._TT["INFO"] = "Apie kalendorių";

Calendar._TT["ABOUT"] =
"DHTML Datos/Laiko Parinkėjas\n" +
"(c) dynarch.com 2002-2005 / Author: Mihai Bazon\n" + // don't translate this this ;-)
"Naujausia versija: http://www.dynarch.com/projects/calendar/\n" +
"Platinama pagal GNU LGPL. Daugiau informacijos http://gnu.org/licenses/lgpl.html." +
"\n\n" +
"Datos parinkimas:\n" +
"- Naudokite \xab, \xbb mygtukus metų parinkimui\n" +
"- Naudokite " + String.fromCharCode(0x2039) + ", " + String.fromCharCode(0x203a) + " mygtukus mėnesių parinkimui\n" +
"- Užlaikykite pelės mygtuką greitesniam parinkimui.";
Calendar._TT["ABOUT_TIME"] = "\n\n" +
"Laiko parinkimas:\n" +
"- Spauskite ant bet kurios laiko dalies norėdami ją padidinti.\n" +
"- Jei laikysite paspaudę Shift ji mažės.\n" +
"- Arba paspauskite ir tempkite greitam parinkimui.";

Calendar._TT["PREV_YEAR"] = "Praeiti metai (palaikykite paspaudę, jei norite meniu)";
Calendar._TT["PREV_MONTH"] = "Praeitas mėnuo (palaikykite paspaudę, jei norite meniu)";
Calendar._TT["GO_TODAY"] = "Šiandiena";
Calendar._TT["NEXT_MONTH"] = "Kitas mėnuo (palaikykite paspaudę, jei norite meniu)";
Calendar._TT["NEXT_YEAR"] = "Kiti metai (palaikykite paspaudę, jei norite meniu)";
Calendar._TT["SEL_DATE"] = "Išsirinkite datą";
Calendar._TT["DRAG_TO_MOVE"] = "Tempkite norėdami pajudinti";
Calendar._TT["PART_TODAY"] = " (šiandiena)";

// the following is to inform that "%s" is to be the first day of week
// %s will be replaced with the day name.
Calendar._TT["DAY_FIRST"] = "Rodyti %s kaip pirmą savaitės dieną.";

// This may be locale-dependent.  It specifies the week-end days, as an array
// of comma-separated numbers.  The numbers are from 0 to 6: 0 means Sunday, 1
// means Monday, etc.
Calendar._TT["WEEKEND"] = "6,0";

Calendar._TT["CLOSE"] = "Uždaryti";
Calendar._TT["TODAY"] = "Šiandiena";
Calendar._TT["TIME_PART"] = "(Shift-)pelės mygtuko spustelėjimas arba tempimas norint pakeisti reikšmę";

// date formats
Calendar._TT["DEF_DATE_FORMAT"] = "%Y-%m-%d";
Calendar._TT["TT_DATE_FORMAT"] = "%a, %b %e";

Calendar._TT["WK"] = "Sa";
Calendar._TT["TIME"] = "Laikas:";

