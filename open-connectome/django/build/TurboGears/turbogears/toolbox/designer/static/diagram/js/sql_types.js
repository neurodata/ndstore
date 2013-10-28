/*
	WWW SQL Designer, (C) 2005 Ondra Zara, o.z.fw@seznam.cz

    This file is part of WWW SQL Designer.

    WWW SQL Designer is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    WWW SQL Designer is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with WWW SQL Designer; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA	
*/

/* -------------------------- nase obecne datove typy -------------------------- */

var SQL_TYPES_DIVISION = [
	{color:"rgb(218,225,225)",name:"Numeric",count:4},
	{color:"rgb(255,255,255)",name:"Character",count:4},
	{color:"rgb(200,255,200)",name:"Date & Time",count:4},
	{color:"rgb(200,200,255)",name:"Others",count:2}
];

var SQL_TYPES_DEFAULT = [
						"Integer",     		/* 0 */
						"Byte",             /* 1 */
						"Single precision", /* 2 */
						"Double precision", /* 3 */
						"String",           /* 4 */
						"Text",             /* 5 */
						"Binary",           /* 6 */
						"BLOB",             /* 7 */
						"Date",             /* 8 */
						"Time",             /* 9 */
						"Datetime",         /* 10 */
						"Timestamp",        /* 11 */
						"Enum",             /* 12 */
						"Set"               /* 13 */
];

var SQL_TYPES_VALUES = [
	/* defaultni hodnoty */
	0,
	0,
	0,
	0,
	"",
	"",
	"",
	"",
	"1900-01-01",
	"00:00:00",
	"1900-01-01 00:00:00",
	0,
	"",
	""
];

var SQL_TYPES_SPEC = [
	/* potrebuji-li doplnkovy inputbox */
	0,
	0,
	0,
	0,
	1,
	0,
	1,
	0,
	0,
	0,
	0,
	0,
	1,
	1
];
							
/* --------------------------- jejich ekvivalenty v sql ------------------------- */							
							
var SQL_TYPES_MYSQL = [ 
						"INTEGER",    /* 0 */
						"TINYINT",    /* 1 */
						"FLOAT",      /* 2 */
						"DOUBLE",     /* 3 */
						"CHAR",       /* 4 */
						"MEDIUMTEXT", /* 5 */
						"VARBINARY",  /* 6 */
						"BLOB",       /* 7 */
						"DATE",       /* 8 */
						"TIME",       /* 9 */
						"DATETIME",   /* 10 */
						"TIMESTAMP",  /* 11 */
						"ENUM",       /* 12 */
						"SET",        /* 13 */
];

/* --------------------------- fallback pro zname i nezname typy ------------------- */
						
var SQL_FALLBACK_MYSQL = new Object();
	SQL_FALLBACK_MYSQL["CHAR"] = 4;
	SQL_FALLBACK_MYSQL["VARCHAR"] = 4;
	SQL_FALLBACK_MYSQL["TINYTEXT"] = 5;
	SQL_FALLBACK_MYSQL["TEXT"] = 5;
	SQL_FALLBACK_MYSQL["BLOB"] = 7;
	SQL_FALLBACK_MYSQL["MEDIUMTEXT"] = 5;
	SQL_FALLBACK_MYSQL["MEDIUMBLOB"] = 7;
	SQL_FALLBACK_MYSQL["LONGTEXT"] = 5;
	SQL_FALLBACK_MYSQL["LONGBLOB"] = 7;
	SQL_FALLBACK_MYSQL["TINYINT"] = 1;
	SQL_FALLBACK_MYSQL["SMALLINT"] = 0;
	SQL_FALLBACK_MYSQL["MEDIUMINT"] = 0;
	SQL_FALLBACK_MYSQL["INT"] = 0;
	SQL_FALLBACK_MYSQL["INTEGER"] = 0;
	SQL_FALLBACK_MYSQL["BIGINT"] = 0;
	SQL_FALLBACK_MYSQL["FLOAT"] = 2;
	SQL_FALLBACK_MYSQL["DOUBLE"] = 3;
	SQL_FALLBACK_MYSQL["DECIMAL"] = 3;
	SQL_FALLBACK_MYSQL["DATE"] = 8;
	SQL_FALLBACK_MYSQL["TIME"] = 9;
	SQL_FALLBACK_MYSQL["DATETIME"] = 10;
	SQL_FALLBACK_MYSQL["TIMESTAMP"] = 11;
	SQL_FALLBACK_MYSQL["ENUM"] = 12;
	SQL_FALLBACK_MYSQL["SET"] = 13;
