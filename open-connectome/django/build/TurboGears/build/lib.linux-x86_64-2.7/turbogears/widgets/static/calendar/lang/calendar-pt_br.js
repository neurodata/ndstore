// Calendar i18n
// Language: pt-br (Portuguese, Brazil)
// Encoding: utf-8
// Author: Adalberto Machado <betosm@terra.com.br>, Jorge Godoy <godoy@g2ctech.com>
// Distributed under the same terms as the calendar itself.

// full day names
Calendar._DN = new Array
("Domingo",
 "Segunda",
 "Terça",
 "Quarta",
 "Quinta",
 "Sexta",
 "Sábado",
 "Domingo");

// short day names
Calendar._SDN = new Array
("Dom",
 "Seg",
 "Ter",
 "Qua",
 "Qui",
 "Sex",
 "Sáb",
 "Dom");

// First day of the week. "0" means display Sunday first.
Calendar._FD = 0;

// full month names
Calendar._MN = new Array
("Janeiro",
 "Fevereiro",
 "Março",
 "Abril",
 "Maio",
 "Junho",
 "Julho",
 "Agosto",
 "Setembro",
 "Outubro",
 "Novembro",
 "Dezembro");

// short month names
Calendar._SMN = new Array
("Jan",
 "Fev",
 "Mar",
 "Abr",
 "Mai",
 "Jun",
 "Jul",
 "Ago",
 "Set",
 "Out",
 "Nov",
 "Dez");

// tooltips
Calendar._TT = {};
Calendar._TT["INFO"] = "Sobre o calendário";

Calendar._TT["ABOUT"] =
"DHTML Date/Time Selector\n" +
"(c) dynarch.com 2002-2005 / Author: Mihai Bazon\n" + // don't translate this this ;-)
"Ultima versão visite: http://www.dynarch.com/projects/calendar/\n" +
"Distribuído sobre GNU LGPL.  Veja http://gnu.org/licenses/lgpl.html para detalhes." +
"\n\n" +
"Seleção de data:\n" +
"- Use os botões \xab, \xbb para selecionar o ano\n" +
"- Use os botões " + String.fromCharCode(0x2039) + ", " + String.fromCharCode(0x203a) + " para selecionar o mes\n" +
"- Segure o botão do mouse em qualquer um desses botões para seleção rápida.";
Calendar._TT["ABOUT_TIME"] = "\n\n" +
"Seleção de hora:\n" +
"- Clique em qualquer parte da hora para incrementar\n" +
"- ou Shift-click para decrementar\n" +
"- ou clique e segure para seleção rápida.";

Calendar._TT["PREV_YEAR"] = "Ano ant. (segure para menu)";
Calendar._TT["PREV_MONTH"] = "Mês ant. (segure para menu)";
Calendar._TT["GO_TODAY"] = "Hoje";
Calendar._TT["NEXT_MONTH"] = "Próx. mes (segure para menu)";
Calendar._TT["NEXT_YEAR"] = "Próx. ano (segure para menu)";
Calendar._TT["SEL_DATE"] = "Selecione a data";
Calendar._TT["DRAG_TO_MOVE"] = "Arraste para mover";
Calendar._TT["PART_TODAY"] = " (hoje)";

// the following is to inform that "%s" is to be the first day of week
// %s will be replaced with the day name.
Calendar._TT["DAY_FIRST"] = "Mostre %s primeiro";

// This may be locale-dependent.  It specifies the week-end days, as an array
// of comma-separated numbers.  The numbers are from 0 to 6: 0 means Sunday, 1
// means Monday, etc.
Calendar._TT["WEEKEND"] = "0,6";

Calendar._TT["CLOSE"] = "Fechar";
Calendar._TT["TODAY"] = "Hoje";
Calendar._TT["TIME_PART"] = "(Shift-)Click ou arraste para mudar valor";

// date formats
Calendar._TT["DEF_DATE_FORMAT"] = "%d/%m/%Y";
Calendar._TT["TT_DATE_FORMAT"] = "%a, %e %b";

Calendar._TT["WK"] = "sem.";
Calendar._TT["TIME"] = "Hora:";
