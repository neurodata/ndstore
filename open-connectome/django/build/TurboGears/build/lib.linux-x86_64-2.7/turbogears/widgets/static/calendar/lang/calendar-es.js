// Calendar i18n
// Language: es (Spanish)
// Encoding: any
// Author: Servilio Afre Puentes <servilios@yahoo.com>
// Distributed under the same terms as the calendar itself.

// full day names
Calendar._DN = new Array
("Domingo",
 "Lunes",
 "Martes",
 "Mi\xe9rcoles",
 "Jueves",
 "Viernes",
 "S\xe1bado",
 "Domingo");

// short day names
Calendar._SDN = new Array
("Dom",
 "Lun",
 "Mar",
 "Mi\xe9",
 "Jue",
 "Vie",
 "S\xe1b",
 "Dom");

// First day of the week. "0" means display Sunday first, "1" means display
// Monday first, etc.
Calendar._FD = 1;

// full month names
Calendar._MN = new Array
("Enero",
 "Febrero",
 "Marzo",
 "Abril",
 "Mayo",
 "Junio",
 "Julio",
 "Agosto",
 "Septiembre",
 "Octubre",
 "Noviembre",
 "Diciembre");

// short month names
Calendar._SMN = new Array
("Ene",
 "Feb",
 "Mar",
 "Abr",
 "May",
 "Jun",
 "Jul",
 "Ago",
 "Sep",
 "Oct",
 "Nov",
 "Dic");

// tooltips
Calendar._TT = {};
Calendar._TT["INFO"] = "Acerca del calendario";

Calendar._TT["ABOUT"] =
"Selector DHTML de Fecha/Hora\n" +
"(c) dynarch.com 2002-2005 / Author: Mihai Bazon\n" + // don't translate this this ;-)
"Para conseguir la \xfaltima versi\xf3n visite: http://www.dynarch.com/projects/calendar/\n" +
"Distribuido bajo licencia GNU LGPL. Visite http://gnu.org/licenses/lgpl.html para m\xe1s detalles." +
"\n\n" +
"Selecci\xf3n de fecha:\n" +
"- Use los botones \xab, \xbb para seleccionar el a\xf1o\n" +
"- Use los botones " + String.fromCharCode(0x2039) + ", " + String.fromCharCode(0x203a) + " para seleccionar el mes\n" +
"- Mantenga pulsado el rat\xf3n en cualquiera de estos botones para una selecci\xf3n r\xe1pida.";
Calendar._TT["ABOUT_TIME"] = "\n\n" +
"Selecci\xf3n de hora:\n" +
"- Pulse en cualquiera de las partes de la hora para incrementarla\n" +
"- o pulse las may\xfasculas mientras hace clic para decrementarla\n" +
"- o haga clic y arrastre el rat\xf3n para una selecci\xf3n m\xe1s r\xe1pida.";

Calendar._TT["PREV_YEAR"] = "A\xf1o anterior (mantener para men\xfa)";
Calendar._TT["PREV_MONTH"] = "Mes anterior (mantener para men\xfa)";
Calendar._TT["GO_TODAY"] = "Ir a hoy";
Calendar._TT["NEXT_MONTH"] = "Mes siguiente (mantener para men\xfa)";
Calendar._TT["NEXT_YEAR"] = "A\xf1o siguiente (mantener para men\xfa)";
Calendar._TT["SEL_DATE"] = "Seleccionar fecha";
Calendar._TT["DRAG_TO_MOVE"] = "Arrastrar para mover";
Calendar._TT["PART_TODAY"] = " (hoy)";

// the following is to inform that "%s" is to be the first day of week
// %s will be replaced with the day name.
Calendar._TT["DAY_FIRST"] = "Hacer %s primer d\xeda de la semana";

// This may be locale-dependent.  It specifies the week-end days, as an array
// of comma-separated numbers.  The numbers are from 0 to 6: 0 means Sunday, 1
// means Monday, etc.
Calendar._TT["WEEKEND"] = "0,6";

Calendar._TT["CLOSE"] = "Cerrar";
Calendar._TT["TODAY"] = "Hoy";
Calendar._TT["TIME_PART"] = "(May\xfascula-)Clic o arrastre para cambiar valor";

// date formats
Calendar._TT["DEF_DATE_FORMAT"] = "%d/%m/%Y";
Calendar._TT["TT_DATE_FORMAT"] = "%A, %e de %B de %Y";

Calendar._TT["WK"] = "sem";
Calendar._TT["TIME"] = "Hora:";

