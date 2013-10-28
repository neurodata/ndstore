var Widget={};
Widget.imagedir='/tg_static/images/';
Widget.exists = function(val)
{
  return typeof(val) != 'undefined';
}

Widget.renderHandler = function(func,params)
{
  var p='';
  for(var i=0;i<params.length;i++)
  {
    if(p!='')p+=',';
    p+="'"+ params[i] +"'";
  }
  return func +'('+ p +')';
}

/*********************************** GRID ****************************/
Widget.grid ={};
Widget.grid.oddColor = 'edf3fe';
Widget.grid.evenColor = 'ffffff';
Widget.grid.highlightColor = 'D9DFE9';

Widget.grid.render = function(id,content)
{
  var headers = (Widget.exists(content['headers']))? Widget.grid.renderHeader(id,content):'';
  var rows = (Widget.exists(content['rows']))? Widget.grid.renderRows(id,content):'';

  return TABLE({'id':id,'class':'grid','border':'0','cellpadding':'3','cellspacing':'1'},
                THEAD(null,headers), 
                rows
               );
}
Widget.grid.renderHeader = function(id,content)
{
  var headers = content['headers'];
  var actions = Widget.exists(content.actions)? content.actions:{};

  var htr = TR(null);
  var lastActiveCell= headers.length -1;
  for(var i=headers.length -1;i >= 0;i--)
  {
    var cell = headers[i];
    var column_name = (Widget.exists(cell.column))? cell.column:cell;
    if(Widget.columnIsHidden(content,column_name)) continue;
    lastActiveCell = i;
    break;
  }
  for(var i=0;i < headers.length;i++)
  {
    var cell = headers[i];
    var column_name = (Widget.exists(cell.column))? cell.column:cell;
    var label = (Widget.exists(cell.label))? cell.label:column_name; 
    var props = {'id':'TH_'+ id +'_'+ column_name,'class':'heading'};
    var sortIcon = '';

    if(Widget.columnIsHidden(content,column_name)) continue;
    if(Widget.exists(cell.sort))
    {
      sortIcon = IMG({'id':'TH_IMG_'+ id +'_'+ column_name,
                      'src':Widget.imagedir +'arrow_'+ cell.sort +'_small.png',
                      'border':'0'});
    }
    if(Widget.exists(actions.sort)) 
    {
      var sortOrder = (Widget.exists(cell.sort))? cell.sort:'down';
      props = {'onclick':actions.sort +"('"+ column_name +"','"+ sortOrder +"')",
               'class':'pointer heading',
               'title':'Sort by '+ label};
      label = SPAN(null,sortIcon,label);
    }
    if(i==lastActiveCell && 
       !(Widget.exists(actions.remove) || Widget.exists(actions.edit) ) &&
       Widget.exists(actions.column_management)) label = SPAN(null,Widget.grid.manageColumns(id,content),label);
    htr.appendChild(TH(props,label));
  }
  if(Widget.exists(actions.remove)  || Widget.exists(actions.edit))
  {
    var cm = (Widget.exists(actions.column_management))? SPAN(null,Widget.grid.manageColumns(id,content)):'';
    htr.appendChild( TH({'id':'TH_'+ id,'class':'heading','style':'width:40px;'},cm));
  }

  if(!htr.hasChildNodes() && Widget.exists(actions.column_management)) 
  {
    props = {'id':'TH_'+ id +'_column_manage','class':'heading'};
    htr.appendChild(TH(props,
                       SPAN(null,Widget.grid.manageColumns(id,content))
                      )
                    );
  }
  return htr;
}

Widget.grid.manageColumns = function(id,content)
{
  var headers = content['headers'];
  var dropDown = UL({'id':'column_chooser_list','class':'column_chooser_list'});

  for(var i=0;i < headers.length;i++)
  {
    var cell = headers[i];
    var column_name = (Widget.exists(cell.column))? cell.column:cell;
    var label = (Widget.exists(cell.label))? cell.label:column_name; 

    var icon = '';
    if(!Widget.columnIsHidden(content,column_name))
    {
      icon = IMG({'border':'0','src':Widget.imagedir+'save.png'});
    }
    var p = content.actions.column_management.params.concat(column_name); 
    var action= 'javascript:'+ Widget.renderHandler(content.actions.column_management['function'],p);
    dropDown.appendChild( LI({'onclick':action},A({'href':'#'},icon,label)) );
  }
  return SPAN({'id':'column_chooser_'+ id,'float':'right'},
            A({'href':'#','class':'column_chooser_link',
               'onmouseover':'document.getElementById("column_chooser_list").style.display="block"', 
               'onmouseout':'document.getElementById("column_chooser_list").style.display="none"' 
              },
               IMG({'src':Widget.imagedir+'column_chooser.png','border':'0'}),
               dropDown
             )
           );
}
Widget.columnIsHidden = function(content,column_name)
{
  if(!Widget.exists(content['hidden_columns'])) return false; 
  for(var i=0;i< content['hidden_columns'].length;i++)
  {
    if(column_name==content['hidden_columns'][i]) return true;
  }
  return false;
}
Widget.grid.renderRows = function(id,content) 
{
  var rows = content['rows'];
  var actions = Widget.exists(content.actions)? content.actions:{};
  var tb = TBODY(null);
  for(var i=0;i < rows.length;i++)
  {
    var row= rows[i];
    var row_id = (Widget.exists(row[0].value))? row[0].value:row[0];
    var cursor =(Widget.exists(actions.select))? ';cursor:pointer':'';
    var color = (i % 2 == 0)? Widget.grid.oddColor:Widget.grid.evenColor;
    var gtr = TR( {
                   'id':'TR_'+ id +'_'+ row_id,
                   'style':'background-color:#'+ color + cursor, 
                   'class':(i % 2 == 0)?'odd':'even',
                   'onmouseover':'Widget.grid.highlight(this,true)',
                   'onmouseout':'Widget.grid.highlight(this,false,"'+ color +'")'
                  }
                );

    for(var j=0;j < row.length;j++)
    {
      var cell_value = (Widget.exists(row[j].value))? row[j].value:row[j];
      var column_name = (Widget.exists(row[j].column))? row[j].column:cell_value;
      if(Widget.columnIsHidden(content,column_name)) continue;
      var cellid = 'TD_'+ id +'_'+ row_id +'_'+ column_name;
      var props = {'id':cellid,'valign':'top'};
      if(Widget.exists(actions.select))
      {
        var p = actions.select.params.concat(row_id); 
        props={'onclick':Widget.renderHandler(actions.select['function'],p),
               'class':'pointer',
               'nowrap':'nowrap',
               'valign':'top',
               'id':cellid,
               'title':'Select row' };
      }
      gtr.appendChild( TD(props,cell_value));
    }
    if(Widget.exists(actions.remove) || Widget.exists(actions.edit) ) gtr.appendChild( Widget.grid.renderRowActionsLink(actions,row_id) );
    tb.appendChild(gtr);
  }
  return tb;
}
Widget.grid.renderRowActionsLink = function(actions,id)
{
  var rem='';
  var ed='';
  if(Widget.exists(actions.remove))
  {
    var p = actions.remove.params.concat([id]);
    rem= A({'href':'javascript:'+ Widget.renderHandler(actions.remove['function'],p),'title':'Remove Row'},
               IMG({'src':Widget.imagedir+'remove.png','border':'0'})
              );
  }
  if(Widget.exists(actions.edit))
  {
    var q = actions.edit.params.concat([id]);
    ed = A({'href':'javascript:'+ Widget.renderHandler(actions.edit['function'],q),'title':'Edit Row'},
               IMG({'src':Widget.imagedir+'edit.png','border':'0'})
              );
  }
  return TD({'align':'right'},ed,rem);
}
Widget.grid.highlight = function(el,state,originalColor)
{
  if(state) { el.style.backgroundColor = '#'+ Widget.grid.highlightColor; }
  else { el.style.backgroundColor = '#'+ originalColor; }
}
/*********************************** SELECT ****************************/
Widget.select = {}
Widget.select.load = function(id,content)
{
  var list= document.getElementById(id);
  if(!Widget.exists(list))
  {
    alert('Are you shure the id for the list is correct?');
    return;
  }
  for(var i=list.options.length-1;i>=0;i--) list.options[i] = null;
  for(var i=0;i<content.options.length;i++)
  {
    var opt = content.options[i];
    var value = (Widget.exists(opt.value))? opt.value:opt;
    var label = (Widget.exists(opt.label))? opt.label:value;
    var selected = (Widget.exists(opt.selected))? true:false;
    var defaultSelected = false;
    list.options[i]= new Option(label,
                                value,
                                defaultSelected,
                                selected);
  }
}
Widget.select.render = function(id,content)
{
  var sel= createDOM('SELECT',{'name':id,'id':id});
  for(var i=0;i<content.options.length;i++)
  {
    var props = {'value':content.options[i].value};
    if(Widget.exists(content.options[i].selected)) props['selected'] = 'selected';
    var opt = createDOM('OPTION',props,content.options[i].label);
    sel.appendChild(opt);
  }
  return sel;
}
Widget.select.removeSelectedOptions = function(list)
{
  if(list.selectedIndex==-1) return;
  for(var i=list.options.length-1;i >=0;i--)
  {
    if(list.options[i]!=null && list.options[i].selected) list.options[i]=null;
  }
}
Widget.select.addSelectedOptionsFromSourceToDestination = function(src,dest)
{
  if(src.selectedIndex==-1) return;
  var newList = [];
  for(var i=0;i<dest.options.length;i++)
  {
    if(dest.options[i]==null) continue;
    newList[newList.length]= new Option(dest.options[i].text,
                                        dest.options[i].value,
                                        dest.options[i].defaultSelected,
                                        dest.options[i].selected);
  }
  for(var i=0;i<src.options.length;i++)
  {
    if(src.options[i]==null || src.options[i].selected==false) continue;
    if(Widget.select.hasValue(dest,src.options[i].value)) continue;
    newList[newList.length]= new Option(src.options[i].text,
                                        src.options[i].value,
                                        src.options[i].defaultSelected,
                                        src.options[i].selected);
  }
  for(var i=0;i<dest.options.length;i++) dest.options[i] = null;
  for(var i=0;i<newList.length;i++)
  {
    dest.options[i]=newList[i];
  }
}
Widget.select.getSelections = function(list)
{
  var values = [];
  for(var i=0;i < list.options.length;i++) 
  {
    if(list.options[i].selected) values[values.length] =list.options[i].value;
  }
  if(values.length > 0) return values;
}
Widget.select.getOptionValuesAsCSV = function(list)
{
  var csv='';
  for(var i=0;i < list.options.length;i++) 
  {
    if(csv!='')csv+=',';
    csv+=list.options[i].value;
  }
  return csv;
}
Widget.select.getSelectionsAsCSV = function(list)
{
  var values = Widget.select.getSelections(list);
  var csv='';
  for(var i=0;i < values.length;i++) 
  {
    if(csv!='')csv+=',';
    csv+=values[i];
  }
  return csv;
}
Widget.select.hasValue= function(list,value)
{
  for(var i=0;i<list.options.length;i++)
  {
    if(list.options[i].value==value) return true;
  } 
  return false;
}
/*********************************** ICON LABEL ****************************/
Widget.iconLabel ={}
Widget.iconLabel.render = function(name,title,action,params)
{
   return A({
             'href':Widget.renderHandler(action,params), 
             'title':title,
             'class':'discloser'
             },
             IMG({'border':'0','style':'margin-right:5px;margin-left:10px','align':'absbottom',
                  'src':Widget.imagedir + name +'.png'} ),
             title
            );
}
Widget.pickDate = function(field_name)
{
    var cal = new Calendar(1,null,Widget.date_selecting,Widget.date_closing);
    cal.showsTime = false;
    cal.setDateFormat('%Y-%m-%d');
    cal.create();
    cal.date_field = document.getElementById(field_name);
    if (cal.date_field && typeof cal.date_field.value == "string") {
      cal.parseDate(cal.date_field.value);
    }
    cal.showAtElement(cal.date_field,'Br')
}
Widget.pickDateTime = function(field_name)
{
    var cal = new Calendar(1,null,Widget.date_selecting,Widget.date_closing);
    cal.showsTime = true;
    cal.time24 = true;
    cal.setDateFormat('%Y-%m-%d %H:%M');
    cal.create();
    cal.date_field = document.getElementById(field_name);
    if (cal.date_field && typeof cal.date_field.value == "string") {
      cal.parseDate(cal.date_field.value);
    }
    cal.showAtElement(cal.date_field,'Br')
}
Widget.date_selecting = function (calendar,my_date)
{
  calendar.date_field.value = my_date;
  if (calendar.dateClicked) {
    calendar.callCloseHandler();
  }
}
Widget.date_closing= function(calendar)
{
  calendar.destroy();
}
