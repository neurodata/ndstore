// Calendar i18n
// Language: ja (Japanese)
// Encoding: utf-8
// Distributed under the same terms as the calendar itself.

Calendar._DN = new Array
("日曜",
 "月曜",
 "火曜",
 "水曜",
 "木曜",
 "金曜",
 "土曜",
 "日曜");

Calendar._SDN = new Array
("日",
 "月",
 "火",
 "水",
 "木",
 "金",
 "土",
 "日");

Calendar._FD = 0;

Calendar._MN = new Array
("1月",
 "2月",
 "3月",
 "4月",
 "5月",
 "6月",
 "7月",
 "8月",
 "9月",
 "10月",
 "11月",
 "12月");

Calendar._SMN = new Array
("1",
 "2",
 "3",
 "4",
 "5",
 "6",
 "7",
 "8",
 "9",
 "10",
 "11",
 "12");

// tooltips
Calendar._TT = {};
Calendar._TT["INFO"] = "カレンダーについて";

Calendar._TT["ABOUT"] =
"DHTML Date/Time Selector\n" +
"(c) dynarch.com 2002-2005 / Author: Mihai Bazon\n" + // don't translate this this ;-)
"For latest version visit: http://www.dynarch.com/projects/calendar/\n" +
"Distributed under GNU LGPL.  See http://gnu.org/licenses/lgpl.html for details." +
"\n\n" +
"日付の選び方:\n" +
"- 年を選ぶには \xab, \xbb のボタンを使います。\n" +
"- 月を選ぶには " + String.fromCharCode(0x2039) + ", " + String.fromCharCode(0x203a) + " のボタンを使います。\n" +
"- マウスのボタンを押しつづけるとさらに早く選択できます。";
Calendar._TT["ABOUT_TIME"] = "\n\n" +
"時間の選び方:\n" +
"- 時間をクリックすると増やせます。\n" +
"- シフト + クリックで減らせます。\n" +
"- ドラッグするとさらに早く選択できます。";

Calendar._TT["PREV_YEAR"] = "前の年(ホールドでメニュー)";
Calendar._TT["PREV_MONTH"] = "前の月(ホールドでメニュー)";
Calendar._TT["GO_TODAY"] = "本日へ";
Calendar._TT["NEXT_MONTH"] = "次の月(ホールドでメニュー)";
Calendar._TT["NEXT_YEAR"] = "次の年(ホールドでメニュー)";
Calendar._TT["SEL_DATE"] = "日付を選択します";
Calendar._TT["DRAG_TO_MOVE"] = "ドラッグで移動";
Calendar._TT["PART_TODAY"] = " (本日)";

// the following is to inform that "%s" is to be the first day of week
// %s will be replaced with the day name.
Calendar._TT["DAY_FIRST"] = "%s を始めに表示する";

// This may be locale-dependent.  It specifies the week-end days, as an array
// of comma-separated numbers.  The numbers are from 0 to 6: 0 means Sunday, 1
// means Monday, etc.
Calendar._TT["WEEKEND"] = "0,6";

Calendar._TT["CLOSE"] = "閉じる";
Calendar._TT["TODAY"] = "本日を選択";
Calendar._TT["TIME_PART"] = "クリック又はドラッグで増えます。シフトキーを使うと減らせます。";

// date formats
Calendar._TT["DEF_DATE_FORMAT"] = "y-mm-dd";
Calendar._TT["TT_DATE_FORMAT"] = "%m月 %d日 (%a)";

Calendar._TT["WK"] = "週";
Calendar._TT["TIME"] = "時間:";
