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

/*
	strategie: vsichni potomci tabulky musi mit vyplneny atribut parent_number, aby z nich bylo snadno poznat,
	ke kteremu objektu prislusi. Dal musi mit vischni vyplneny typ.
*/


/*
	objekt abstractParent:
		setTitle() - zmena textu v _title
		select(), deselect() - vyber
		select => je-li vybrano
		_title => html element
		_div => html element
*/

function abstractParent_setTitle(text) {
	this._title.innerHTML = text;
}

function abstractParent_destroy() {
	this._div.parentNode.removeChild(this._div);
	if (this._mini) {
		this._mini.parentNode.removeChild(this._mini);
	}
}

function abstractParent_select() {
	this._div.className = this._div.className + " " + this._div.className + "_selected";
	this.selected = true;
}

function abstractParent_deselect() {
	this._div.className = this._div.getAttribute("defaultClassName");
	this.selected = false;
}

function abstractParent(type, parent_number, row_number, className) {
	this._div = document.createElement("div");
	this._title = document.createElement("div");

	this._title.className = "title";
	this._div.className = className;

	this._div.setAttribute("defaultClassName",className);
	this._div.setAttribute("parent_number",parent_number);
	this._div.setAttribute("row_number",row_number);
	this._div.setAttribute("element_type",type);
	
	this._title.setAttribute("parent_number",parent_number);
	this._title.setAttribute("row_number",row_number);
	this._title.setAttribute("element_type",TYPE_TITLE);

	this._div.appendChild(this._title);
	
	this.selected = false;
	this.select = abstractParent_select;
	this.deselect = abstractParent_deselect;
	this.destroy = abstractParent_destroy;
	this.setTitle = abstractParent_setTitle;
/*	universalAttacher(this._div,"mousedown",global_event_mousedown); */
}

/*
	objekt Row
		setPK(), losePK() - primary key
		setFK(), loseFK() - foreign key
		setIndex(), loseIndex() - index
		setNN(), loseNN() - not null
		setDef() - default
		updateTitle() - updatne title="xxx" atribut
		setTitle() - updatne title="xxx" atribut
		setType() - updatne typ a defaultni hodnotu
		updateSpecial() - updatne special
		updateColor() - updatne pozadi dle datoveho typu
		_special - drzadlo na specialni PK a FK, vpravo
		
		pk - je-li primary key
		fk - je-li foreign key
		index - je-li index
		nn - je-li notnull
		def - defaultni hodnota
		type - datovy typ (resp. jeho index)
		spec - delka ci vycet
*/

function Row_setPK() {
	this.pk = 1;
	this.setIndex();
	this.updateTitle();
	this.updateSpecial();
	this._title.style.fontWeight = "bold";
}

function Row_losePK() {
	this.pk = 0;
	this.updateTitle();
	this.updateSpecial();
	this._title.style.fontWeight = "normal";
}

function Row_setFK() {
	this.fk = 1;
	this.updateTitle();
	this.updateSpecial();
}

function Row_loseFK() {
	this.fk = 0;
	this.updateTitle();
	this.updateSpecial();
}

function Row_setNN() {
	this.nn = 1;
	this.updateTitle();
}

function Row_loseNN() {
	this.nn = 0;
	this.updateTitle();
}

function Row_setIndex() {
	this.index = 1;
	this.updateTitle();
	this._title.style.fontStyle = "italic";
}

function Row_loseIndex() {
	this.index = 0;
	this.updateTitle();
	this._title.style.fontStyle = "normal";
}

function Row_updateTitle() {
	str = this._title.innerHTML + ": ";
	str += SQL_TYPES_DEFAULT[this.type];
	if (SQL_TYPES_SPEC[this.type]) {
		str += "(" + this.spec + ")";
	}
	str += ", default: '" + this.def + "'";
	if (this.pk) {
		str += ", Primary key";
	}
	if (this.fk) {
		str += ", Foreign key";
	}
	if (this.nn) {
		str += ", NOT NULL";
	}
	if (this.index) {
		str += ", Index";
	}
	//this._div.setAttribute("title",str);
	//this._title.setAttribute("title",str);
}

function Row_setDef(value) {
	this.def = value;
	this.updateTitle();
}

function Row_setSpec(value) {
	this.spec = value;
	this.updateTitle();
}

function Row_setType(type) {
	this.type = type;
	this.def = SQL_TYPES_VALUES[type];
	this.updateTitle();
	this.updateColor();
}

function Row_updateSpecial() {
	var str = "";
	if (this.pk) str += "PK";
	if (this.pk && this.fk) str += ",";
	if (this.fk) str += "FK";
	this._special.innerHTML = str;
}

function Row_updateColor() {
	var total = 0;
	for (var i=0;i<SQL_TYPES_DIVISION.length;i++) {
		for (var j=0;j<SQL_TYPES_DIVISION[i].count;j++) {
			if (this.type == total) {
				this._div.style.backgroundColor = SQL_TYPES_DIVISION[i].color;
			}
			total++;
		}
	}
}

function Row_appendRelation(relation) {
	var count = get_free_index(this.relations);
	this.relations[count] = relation; /* dame si objekt do pole */
}

function Row_updateRelations() {
	for (var i=0;i<this.relations.length;i++) {
		if (this.relations[i]) {
			this.relations[i].update();
		}
	}
}

function Row_hideRelations() {
	for (var i=0;i<this.relations.length;i++) {
		if (this.relations[i]) {
			this.relations[i].hide();
		}
	}
}

function Row_showRelations() {
	for (var i=0;i<this.relations.length;i++) {
		if (this.relations[i]) {
			this.relations[i].show();
		}
	}
}

function Row_removeRelation(global_index) {
	for (var i=0;i<this.relations.length;i++) {
		if (this.relations[i] && this.relations[i]._div.getAttribute("parent_number") == global_index) {
			this.relations[i] = null;
		}
	}
}

Row.prototype = new abstractParent();
function Row(parent_number,row_number,title,type) {
	this.base = abstractParent;
	this.base(TYPE_ROW, parent_number, row_number, "row");
	this.relations = Array();
	this.setPK = Row_setPK;
	this.losePK = Row_losePK;
	this.setFK = Row_setFK;
	this.loseFK = Row_loseFK;
	this.setIndex = Row_setIndex;
	this.loseIndex = Row_loseIndex;
	this.setNN = Row_setNN;
	this.loseNN = Row_loseNN;
	this.setType = Row_setType;
	this.setSpec = Row_setSpec;
	this.updateTitle = Row_updateTitle;
	this.updateSpecial = Row_updateSpecial;
	this.updateColor = Row_updateColor;
	this.setDef = Row_setDef;
	this.appendRelation = Row_appendRelation;
	this.updateRelations = Row_updateRelations;
	this.showRelations = Row_showRelations;
	this.hideRelations = Row_hideRelations;
	this.removeRelation = Row_removeRelation;
	this.setTitle(title);
	this._title.setAttribute("element_type",TYPE_ROWTITLE);
	this._title.className = "row_title";
	this._special = document.createElement("div");
	this._special.className="special";
	this._special.setAttribute("parent_number",parent_number);
	this._special.setAttribute("row_number",row_number);
	this._sipka = document.createElement("div");
	this._sipka.setAttribute("parent_number",parent_number);
	this._sipka.setAttribute("row_number",row_number);
	this._sipka.className="sipka";
	this._sipka.innerHTML = "&raquo;&nbsp;";
	this._div.insertBefore(this._special,this._title);
	this._div.insertBefore(this._sipka,this._title);
	this.pk = 0;
	this.fk = 0;
	this.index = 0;
	this.def = "";
	this.nn = 0;
	this.spec = "";
	this.setType(type);
	this.updateTitle();
	this.updateColor();
}


/*
	objekt Relation:
		update() - upravi pozice na zaklade pozic otcu
		select(), deselect() - ma svuj vlastni select, neb sestava ze 3 casti
		hover(), dehover() - ma svuj vlastni hover, neb sestava ze 3 casti
		parent_1, parent_2 - divy otcovskych tabulek
		row_1, row_2 - divy relevantnich radek
		number_1, number_2 - indexy do poli relaci v tabulkach
		id - id do globalni tabulky
*/

function Relation_show() {
	this._div.style.visibility = "visible";
}

function Relation_hide() {
	this._div.style.visibility = "hidden";
}

function Relation_update() {
	/* 
		prekresleni car:
		rozlisujeme dva pripady,
 		 a) kdyz maji mezi sebou tabulky horizontalni mezeru,
		 b) kdyz ji nemaji
	*/
	
	/* 
		k napozicovani elementu je potreba techto udaju:
			- start_x, start_y, center_x, start_y
			- center_x, start_y, center_x, end_y
			- center_x, end_y, end_x, end_y
	*/

	var left_table, right_table, left_row, right_row, left_1, left_2, right_1, right_2, width_1, width_2;
	var top_table_1, top_table_2, top_row_1, top_row_2;
	if (parseInt(this.parent_1._div.style.left) < parseInt(this.parent_2._div.style.left)) {
		left_table = this.parent_1._div;
		right_table = this.parent_2._div;
		left_row = this.row_1._div;
		right_row = this.row_2._div;
	} else {
		right_table = this.parent_1._div;
		left_table = this.parent_2._div;
		right_row = this.row_1._div;
		left_row = this.row_2._div;
	}
	/* ted uz vime, ktera tabulka ma levou hranu vic vlevo. spocteme dulezita cisla */
	left_1 = parseInt(left_table.style.left); /* leva hrana leve tabulky */
	left_2 = parseInt(right_table.style.left); /* leva hrana prave tabulky */
	width_1 = parseInt(left_table.offsetWidth); /* sirka leve tabulky */
	width_2 = parseInt(right_table.offsetWidth); /* sirka prave tabulky */
	right_1 = left_1 + width_1; /* prava hrana leve tabulky */
	right_2 = left_2 + width_2; /* prava hrana prave tabulky */
	top_table_1 = parseInt(left_table.style.top); /* horni hrana leve tabulky */
	top_table_2 = parseInt(right_table.style.top); /* horni hrana prave tabulky */
	top_row_1 = Math.round(parseInt(left_row.offsetHeight)/2)+parseInt(left_row.offsetTop); /* posun radku v leve tabulce */
	top_row_2 = Math.round(parseInt(right_row.offsetHeight)/2)+parseInt(right_row.offsetTop); /* posun radku v prave tabulce */
	
	/* nyni detekce mezery... */
	if (right_1 < left_2) {
		/* tabulky mezi sebou maji mezeru, standardni postup */
		var width = left_2 - left_1 - width_1 + RELATION_THICKNESS;
		var start_x = left_1 + width_1 - RELATION_THICKNESS;
		var start_y = top_table_1 + top_row_1;
		var end_x = left_2;
		var end_y = top_table_2 + top_row_2;
		var center_x = start_x + Math.round(width / 2);
		/* korekce kvuli borderu... */
		start_x--;
	} else {
		var diff_1 = Math.abs(left_2 - left_1); /* rozdil vlevo */
		var diff_2 = Math.abs(right_2 - right_1); /* rozdil vlevo */
		if (diff_1 < diff_2 + RELATION_THICKNESS) {
			/* "ucho" povede vlevo od obou tabulek */
			start_x = left_1;
			start_y = top_table_1 + top_row_1;
			end_x = left_2;
			end_y = top_table_2 + top_row_2;
			center_x = start_x - RELATION_OFFSET;
		} else {
			/* "ucho" povede vpravo od obou tabulek */
			start_x = Math.max(right_1, right_2) - RELATION_THICKNESS;
			start_y = (right_1 > right_2 ? top_table_1 + top_row_1 : top_table_2 + top_row_2);
			end_x = Math.min(right_1, right_2) - RELATION_THICKNESS;
			end_y = (right_1 < right_2 ? top_table_1 + top_row_1 : top_table_2 + top_row_2);
			center_x = start_x + RELATION_OFFSET;
			/* korekce kvuli borderu... */
			start_x--;
			end_x--;
		}
	}
	
	
	/* a jedem */
	this.elem_1.style.left = Math.min(start_x, center_x) + "px";
	this.elem_1.style.top = start_y + "px"
	this.elem_1.style.width = Math.abs(center_x - start_x) + "px";
	this.elem_2.style.left = center_x;
	this.elem_2.style.top = Math.min(start_y, end_y);
	this.elem_2.style.height = Math.abs(end_y - start_y) + RELATION_THICKNESS + "px";
	this.elem_3.style.left = Math.min(center_x, end_x) + "px";
	this.elem_3.style.top = end_y + "px"
	this.elem_3.style.width = Math.abs(center_x - end_x) + "px";
}

Relation.prototype = new abstractParent(); 
function Relation(parent_1, row_1, parent_2, row_2, id) {
	this.base = abstractParent;
	this.base(TYPE_RELATION, id, row_1, "relation");
	this._title.parentNode.removeChild(this._title);
	this.update = Relation_update; /* funkce na aktualizaci car */
	this.show = Relation_show; /* ukazani */
	this.hide = Relation_hide; /* schovani */
	this.parent_1 = parent_1; /* prvni rodicovska tabulka */
	this.parent_2 = parent_2; /* druha rodicovska tabulka */
	this.row_1 = row_1; /* prvni rodicovska radka */
	this.row_2 = row_2; /* druha rodicovska radka */
	this.elem_1 = document.createElement("div");
	this.elem_2 = document.createElement("div");
	this.elem_3 = document.createElement("div");
	this.elem_1.style.height = RELATION_THICKNESS;
	this.elem_2.style.width = RELATION_THICKNESS;
	this.elem_3.style.height = RELATION_THICKNESS;
	this.elem_1.setAttribute("element_type",TYPE_RELATION_PART);
	this.elem_2.setAttribute("element_type",TYPE_RELATION_PART);
	this.elem_3.setAttribute("element_type",TYPE_RELATION_PART);
	this._div.appendChild(this.elem_1);
	this._div.appendChild(this.elem_2);
	this._div.appendChild(this.elem_3);
}

/*
	objekt Table:
		moveTo() - posun na zadane souradnice
		addRow() - prida radku
		removeRow() - odebere radku
		selectRow() - vybere radku
		appendRelation() - prida relaci
		removeRelation() - zrusi relaci
		updateWidth() - aktualizuje sirku
		updateMini() - aktualizuje minimapku
		updateShadow() - aktualizuje rozbite stiny
		showRelations() - ukaze relevantni relace
		hideRelations() - schova relevantni relace
		rows => pole radku
		_rows => html drzak radku
		relations => pole relaci, ktere se tykaji teto tabulky
*/



function Table_updateMini() {
	var w = parseInt(this._div.offsetWidth);
	var h = parseInt(this._div.offsetHeight);
	var l = parseInt(this._div.style.left);
	var t = parseInt(this._div.style.top);
	this._mini.style.width = Math.round(w * MAP_SIZE / DESK_SIZE) + "px";
	this._mini.style.height = Math.round(h * MAP_SIZE / DESK_SIZE) + "px";
	this._mini.style.left = Math.round(l * MAP_SIZE / DESK_SIZE) + "px";
	this._mini.style.top = Math.round(t * MAP_SIZE / DESK_SIZE) + "px";
}

function Table_moveTo(x,y) {
	this._div.style.left = x + "px";
	this._div.style.top = y + "px";
	this.updateMini();
}

function Table_addRow(title,type,custom_index) {
	var count = get_free_index(this.rows);
	if (custom_index) count = custom_index;
	var row = new Row(this.number,count,title,type); /* to je ona */
	this.rows[count] = row; /* dame si objekt do pole */
	this._rows.appendChild(row._div); /* a pridame i do HTML stromu */
	this.updateWidth();
	var x = this;
	var endFuncRef = function() {
		x.updateMini();
		x.updateShadow();
		for (var i=0;i<x.rows.length;i++) {
			if (x.rows[i]) {
				x.rows[i].updateRelations();
				x.rows[i].showRelations();
			}
		}
	}
	//start_animation(row._div,1,endFuncRef);
    //setTimeout(endFuncRef,10);
	return row;
}

function Table_removeRow(index,no_animation) {
	/* neprijdeme tim o nejake pekne relace? */
	var row = this.rows[index];
	for (var i=0;i<row.relations.length;i++) {
		if (row.relations[i]) {
			var rel_index = row.relations[i]._div.getAttribute("parent_number");
			remove_relation(rel_index);
		}
	}
	var x = this;
	var endFuncRef = function() {
		x.rows[index].destroy(); 
		x.rows[index] = null;
		x.updateMini();
		x.updateShadow();
		for (var i=0;i<x.rows.length;i++) {
			if (x.rows[i]) {
				x.rows[i].updateRelations();
				x.rows[i].showRelations();
			}
		}
	}
	if (no_animation) {
		endFuncRef();
	} else {
		start_animation(row._div,-1,endFuncRef);
	}
	var last = -1;
	for (var i=0;i<this.rows.length;i++) {
		if (this.rows[i] && i != index) {
			last = i;
		}
	}
	if (last != -1) {
		this.selectRow(last);
	}
	return (last == -1 ? false : this.rows[last]);
}

function Table_selectRow(index) {
	if (this.selectedRow) {
		this.selectedRow.deselect();
	}
	this.selectedRow = this.rows[index];
	this.selectedRow.select();
}


function Table_updateWidth() {
	var index;
	var orig = parseInt(this._div.style.width);
	var max=this._title.innerHTML.length;
	for (var i=0;i<this.rows.length;i++) {
		if (this.rows[i]) {
			if (this.rows[i]._title.innerHTML.length > max) {
				max = this.rows[i]._title.innerHTML.length;
			}
		}
	}
	var new_ = Math.max(TABLE_WIDTH,80+max*LETTER_WIDTH);
	this._div.style.width = new_ + "px";
	if (new_ != orig) {
		this.updateMini();
		/* pokud jsme tabulce zmenili rozmery, musime aktualizovat relace */
		for (var i=0;i<this.rows.length;i++) {
			if (this.rows[i]) {
				this.rows[i].updateRelations();
			} /* if ziva relace */
		} /* for vsechny relace */
	} /* if hybli sme sirkou */
}

function Table_hideShadow() {
	this.s1.className= "";
	this.s2.className= "";
	this.s3.className= "";
}

function Table_updateShadow() {
	this.hideShadow();
	this.s1.className= "shadow_right";
	this.s2.className= "shadow_bottom";
	this.s3.className = "shadow_corner";
}

function Table_setPK(index) {
	/* primary key */
	var old_primary = -1;
	for (var i=0;i<this.rows.length;i++) {
		if (this.rows[i]) {
			if (this.rows[i].pk) {
				old_primary = i;
				this.rows[i].losePK();
			}
		}
	}
	if (old_primary != -1) {
		/* predtim uz nejaka radka byla primary. pak je mozna potreba predelat relaci. */
		var old = this.rows[old_primary];
		for (var j=0;j<old.relations.length;j++) {
			if (old.relations[j]) {
				if (old.relations[j].parent_1._div.getAttribute("parent_number") == this.number 
					&& old.relations[j].row_1._div.getAttribute("row_number") == old_primary) {
					var count = get_free_index(this.rows[index].relations);
					this.rows[index].relations[count] = old.relations[j];
					this.rows[index].relations[count].row_1 = this.rows[index];
					this.rows[index].relations[count].update();
					old.relations[j] = null;
					if (this.rows[index].relations[count].row_2._div.getAttribute("row_number") == index) {
						/* pokud ted mame relaci, ktera vede sama na sebe, zrusime ji */
						remove_relation(this.rows[index].relations[count]._div.getAttribute("parent_number"));
					} 
				} /* pokud je to relace, ktera tam zacinala */
			} /* pokud relace not null */
		} /* for vsechny relace v te stare radce */
	} /* pokud uz existovala jina PK radka */
	this.rows[index].setPK();
}


Table.prototype = new abstractParent();
function Table(x,y,number,_zIndex,title) {
	this.base = abstractParent;
	this.base(TYPE_TABLE, number, 0, "table");
	this._div.style.width = TABLE_WIDTH + "px";
	this.rows = Array();
	this.selectRow = Table_selectRow;
	this.moveTo = Table_moveTo;
	this.addRow = Table_addRow;
	this.removeRow = Table_removeRow;
	this.updateWidth = Table_updateWidth;
	this.updateMini = Table_updateMini;
	this.updateShadow = Table_updateShadow;
	this.hideShadow = Table_hideShadow;
	this.setPK = Table_setPK;

	this.setTitle(title);
	this._title.className = "table_title";
	this.number = number;
	this.selectedRow = null;

	this._rows = document.createElement("div"); /* sem pujdou radky */
	this._rows.className = "rows"
	
	this._mini = document.createElement("div");
	this._mini.className = "mini";
	this._mini.setAttribute("element_type",TYPE_MAP);
	
	/* provazani do stromove struktury */
	var map = document.getElementById("map");
	map.appendChild(this._mini);
	this._div.appendChild(this._rows);
	
	this.s1 = document.createElement("div");
	this.s2 = document.createElement("div");
	this.s3 = document.createElement("div");
	

	this._div.appendChild(this.s1);
	this._div.appendChild(this.s2);
	this._div.appendChild(this.s3);
	this.updateShadow();
	
	this._div.style.zIndex = _zIndex;
	this.moveTo(x,y);
	this.updateWidth();
}


/*
	objekt TableAdmin:
		cudliky na pridani a smazani tabulek, input na zmenu nazvu
		changeName() - zmena nadpisu tabulky
		manageTable, loseTable() - vybrani a odvybrani tabulky
		addTable, delTable() - zruseni a vytvoreni tabulky
	
*/



function TableAdmin_changeName() {
	this.table_ref.updateWidth();
}

function TableAdmin_manageTable(table) {
	this.table_ref = table;
}

function TableAdmin_loseTable() {
	this.table_ref = null;
}

function getLateFunc(obj, methodName) {
	return (function() {
			return obj[methodName](this);
	});
}

function TableAdmin() {
	this.manageTable = TableAdmin_manageTable;
	this.loseTable = TableAdmin_loseTable;
	this.changeName = TableAdmin_changeName;
	this.last_number = 0;
	this.table_ref = null; 
	this.loseTable();
}

/*
	objekt RowAdmin:
		cudliky na pridani a smazani radek, resp. budoucich sloupcu
		changeName() - zmena nazvu
		manageTable, loseTable() - vybrani a odvybrani tabulky
		manageRow, loseRow() - vybrani a odvybrani radku
		addRow, delRow() - zruseni a vytvoreni radku
		upRow, downRow() - presun nahoru a dolu
*/

function RowAdmin_upRow() {
	var div = this.row_ref._div;
	var root = div.parentNode;
	var prev = div.previousSibling;
	if (prev) {
		root.insertBefore(div,prev);
		var idx = prev.getAttribute("row_number");
		this.row_ref.updateRelations();
		this.table_ref.rows[idx].updateRelations();
	}
}

function RowAdmin_downRow() {
	var div = this.row_ref._div;
	var root = div.parentNode;
	var next = div.nextSibling;
	if (next) {
		root.insertBefore(next,div);
		var idx = next.getAttribute("row_number");
		this.row_ref.updateRelations();
		this.table_ref.rows[idx].updateRelations();
	}
}

function RowAdmin_addRow() {
	if (!this.table_ref) { return; }
	var row = this.table_ref.addRow("row",4);
	row.setNN();
	row.setSpec(32);
	this.manageRow(row);
	if (this.table_ref.selectedRow) {
		this.table_ref.selectedRow.deselect();
	}
	this.table_ref.selectedRow = row;
	row.select();
}

function RowAdmin_delRow() {
	if (!this.row_ref) { return; }
	var title = this.row_ref._title.innerHTML;
	var title2 = this.table_ref._title.innerHTML;
	if (!confirm("Really delete row '"+title+"' from table '"+title2+"' ?")) { return; }
	var index = parseInt(this.row_ref._div.getAttribute("row_number"));
	var last_row = this.table_ref.removeRow(index);
	if (last_row) {
		this.manageRow(last_row); 
	} else {
		this.loseRow();
	}

}

function RowAdmin_changeName() {
	this.table_ref.updateWidth();
	this.row_ref.updateTitle();
}

function RowAdmin_changeDef() {
	return;
}

function RowAdmin_changeSpec() {
	return;
}

function RowAdmin_manageTable(table) {
	var num=-1;
	if (this.table_ref) {
		num = this.table_ref.number;
	}
	if (num != table.number) {
		/* pokud jsme vybrali nejakou, ktera predtim nebyla vybrana */
		this.loseRow();
		this.table_ref = table; /* reference na tabulku */
	}
}

function RowAdmin_loseTable(table) {
	/* ztratili jsme tabulku */
	this.loseRow();
	this.table_ref = null;

}

function RowAdmin_manageRow(row) {
    return;
}

function RowAdmin_loseRow() {
    return;
}

function RowAdmin_setPK() {
	/* primary key */
	if (!this.row_ref) { return; }
	var index = parseInt(this.row_ref._div.getAttribute("row_number"));
	this.table_ref.setPK(index);
}

function RowAdmin_changeType() {
    return;
}

function RowAdmin_changeIndex() {
	/* zmena index on/off */
	if (!this.row_ref) { return; }
	if (this.row_ref.index) {
		this.row_ref.loseIndex();
	} else {
		this.row_ref.setIndex();
	}
}

function RowAdmin_changeNN() {
	/* zmena index on/off */
	if (!this.row_ref) { return; }
	if (this.row_ref.nn) {
		this.row_ref.loseNN();
	} else {
		this.row_ref.setNN();
	}
}

function RowAdmin() {
	this.manageRow = RowAdmin_manageRow;
	this.loseRow = RowAdmin_loseRow;
	this.changeName = RowAdmin_changeName;
	this.changeSpec = RowAdmin_changeSpec;
	this.changeDef = RowAdmin_changeDef;
	this.addRow = RowAdmin_addRow;
	this.delRow = RowAdmin_delRow;
	this.upRow = RowAdmin_upRow;
	this.downRow = RowAdmin_downRow;
	this.manageTable = RowAdmin_manageTable;
	this.loseTable = RowAdmin_loseTable;
	this.setPK = RowAdmin_setPK;
	this.changeType = RowAdmin_changeType;
	this.changeIndex = RowAdmin_changeIndex;
	this.changeNN = RowAdmin_changeNN;
	
	this.last_number = 0; /* pro automaticke cislovani tabulek */
	this.table_ref = null; /* odkaz na prave vybranou tabulku */
	this.row_ref = null; /* odkaz na prave vybranou radku */

	this.loseRow();
}
