// Calendar i18n
// Language: fr (French)
// Encoding: utf-8
// Authors: David Duret, <pilgrim@mala-template.net>
//          Stéphane Raimbault <stephane.raimbault@gmail.com>, 2008
//
// Distributed under the same terms as the calendar itself.

// full day names
Calendar._DN = new Array
("Dimanche",
 "Lundi",
 "Mardi",
 "Mercredi",
 "Jeudi",
 "Vendredi",
 "Samedi",
 "Dimanche");

// short day names
Calendar._SDN = new Array
("Dim.",
 "Lun.",
 "Mar.",
 "Mer.",
 "Jeu.",
 "Ven.",
 "Sam.",
 "Dim.");

// First day of the week. "0" means display Sunday first, "1" means display
// Monday first, etc.
Calendar._FD = 1;

// full month names
Calendar._MN = new Array
("Janvier",
 "Février",
 "Mars",
 "Avril",
 "Mai",
 "Juin",
 "Juillet",
 "Août",
 "Septembre",
 "Octobre",
 "Novembre",
 "Décembre");

// short month names
Calendar._SMN = new Array
("Janv.",
 "Févr.",
 "Mars",
 "Avril",
 "Mai",
 "Juin",
 "Juil.",
 "Août",
 "Sept.",
 "Oct.",
 "Nov.",
 "Déc.");

// tooltips
Calendar._TT = {};
Calendar._TT["INFO"] = "À propos du calendrier";

Calendar._TT["ABOUT"] =
"DHTML Sélecteur de date/heure\n" +
"(c) dynarch.com 2002-2005 / Auteur : Mihai Bazon\n" + // don't translate this this ;-)
"Pour la dernière version, consultez : http://www.dynarch.com/projects/calendar/\n" +
"Distribué sous licence GNU LGPL. Voir http://gnu.org/licenses/lgpl.html pour les détails." +
"\n\n" +
"Séléction de la date :\n" +
"- utilisez les boutons \xab, \xbb  pour sélectionner l\'année\n" +
"- utilisez les boutons " + String.fromCharCode(0x2039) + ", " + String.fromCharCode(0x203a) + " pour sélectionner les mois\n" +
"- maintenez la souris sur n'importe quel bouton pour une sélection plus rapide";
Calendar._TT["ABOUT_TIME"] = "\n\n" +
"Sélection de l\'heure :\n" +
"- cliquez sur heures ou minutes pour incrémenter\n" +
"- ou Maj-Clic pour décrémenter\n" +
"- ou Clic et glisser-déplacer pour une sélection plus rapide";

Calendar._TT["PREV_YEAR"] = "Année préc. (maintenir pour menu)";
Calendar._TT["PREV_MONTH"] = "Mois préc. (maintenir pour menu)";
Calendar._TT["GO_TODAY"] = "Atteindre la date du jour";
Calendar._TT["NEXT_MONTH"] = "Mois suiv. (maintenir pour menu)";
Calendar._TT["NEXT_YEAR"] = "Année suiv. (maintenir pour menu)";
Calendar._TT["SEL_DATE"] = "Sélectionner une date";
Calendar._TT["DRAG_TO_MOVE"] = "Déplacer";
Calendar._TT["PART_TODAY"] = " (aujourd'hui)";

// the following is to inform that "%s" is to be the first day of week
// %s will be replaced with the day name.
Calendar._TT["DAY_FIRST"] = "Afficher %s en premier";

// This may be locale-dependent.  It specifies the week-end days, as an array
// of comma-separated numbers.  The numbers are from 0 to 6: 0 means Sunday, 1
// means Monday, etc.
Calendar._TT["WEEKEND"] = "0,6";

Calendar._TT["CLOSE"] = "Fermer";
Calendar._TT["TODAY"] = "Aujourd'hui";
Calendar._TT["TIME_PART"] = "(Maj-)Clic ou glisser pour modifier la valeur";

// date formats
Calendar._TT["DEF_DATE_FORMAT"] = "%d/%m/%Y";
Calendar._TT["TT_DATE_FORMAT"] = "%A %e %B";

Calendar._TT["WK"] = "Sem.";
Calendar._TT["TIME"] = "Heure :";
