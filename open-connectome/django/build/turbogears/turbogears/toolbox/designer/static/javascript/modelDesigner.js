var nameMsg = 'The name will be converted from mixed-case to undescored-separated to be used as column name.';
var alternateMsg = 'This boolean (default False) indicates if the column can be used as an ID for the field';
var notnullMsg = 'If true, None/NULL is not allowed for this column.';
var uniqueMsg = 'If true, when SQLObject creates a table it will declare this column to be UNIQUE.';
var defaultMsg = 'The default value for this column. Used when creating a new row.';
var dbNameMsg = 'Name of the column in the database.';
var titleMsg = 'Descriptive name for your field';

var designer = {};
designer.currentModel = '';
designer.ordered_models = [];
designer.models = {};
designer.column_types = {
                           'StringCol':{},
                           'IntCol':{},
                           'FloatCol':{},
                           'DateCol':{},
                           'DateTimeCol':{},
                           'BoolCol':{},
                           'EnumCol':{},
                           'DecimalCol':{},
                           'CurrencyCol':{},
                           'BLOBCol':{},
                           'PickleCol':{},
                           'UnicodeCol':{},
                           'MultipleJoin':{},
                           'SingleJoin':{},
                           'ForeignKey':{},
                           'RelatedJoin':{}
                         };
designer.tableRowInput = function(label,name,value,help_tip)
{
   var props = (designer.exists(help_tip))? {'title':help_tip}:null;
   return TR(props,
                TD({'class':'label','valign':'top'},label +' :'),
                TD({'class':'field','valign':'top'},
                    createDOM('INPUT',{'type':'text', 'value':value, 'id':name})
                )
           );
}
designer.tableRowSelect = function(field_name,label,values,value)
{
   var sel = createDOM('SELECT', {'id':field_name});
   for(var i=0;i<values.length;i++)
   {
       var props = {'value':values[i]};
       if(value==values[i]) props['selected']='selected';
       sel.appendChild( createDOM('OPTION',props ,values[i] ));
   }
   return TR(null, TD({'class':'label'},label +' :'), TD({'class':'field'}, sel));
}

designer.tableRowRelationTypes = function(value)
{
    var values = ['MultipleJoin','SingleJoin','RelatedJoin'];
    return designer.tableRowSelect('join_type','relationship type',values,value);
}
designer.tableRowOtherClasses= function(model_name,value)
{
   var values = [''];
   for(var model in designer.sortedModels())
   {
      var m = designer.models[model];
      if(m.name!=model_name) values[values.length]=m.name;
   }
   return designer.tableRowSelect('other_class_name','otherClassName',values,value);
}
designer.tableRowAllClasses= function(value)
{
   var values = [''];

   for(var model in designer.sortedModels())
   {
      var m = designer.models[model];
      values[values.length]=m.name;
   }

   return designer.tableRowSelect('other_class_name','otherClassName',values,value);
}
designer.tableRowBool = function(label,name,value,help_tip)
{
   var tr_props = (designer.exists(help_tip))? {'title':help_tip}:null;
   var sel = createDOM('SELECT', {'id':name});
   var val = ['','True','False'];
   for(var i=0;i<val.length;i++)
   {
       var props = {'value':val[i]};
       if(value==val[i]) props['selected']='selected';
       sel.appendChild( createDOM('OPTION',props ,val[i] ));
   }
   return TR(tr_props,
                TD({'class':'label'},label +' :'),
                TD({'class':'field'}, sel)
           );
}
designer.loadBasicValues = function(model_name,column_name)
{
    var columns = designer.models[model_name].columns;
    var column = (designer.exists(columns[column_name]))? columns[column_name]:{};
    var props = {};
    props['column_label'] =(column_name=='__new__')? '':column_name;
    props['column_title'] = (designer.exists(column['column_title']))? column['column_title']:'';
    props['column_db_name'] = (designer.exists(column['column_db_name']))? column['column_db_name']:'';
    props['column_default'] = (designer.exists(column['column_default']))? column['column_default']:'';
    props['column_length'] = (designer.exists(column['column_length']))? column['column_length']:'';
    props['column_varchar'] = (designer.exists(column['column_varchar']))? column['column_varchar']:'';
    props['column_unique'] = (designer.exists(column['column_unique']))? column['column_unique']:'';
    props['column_not_none'] = (designer.exists(column['column_not_none']))? column['column_not_none']:'';
    props['column_alternate_id'] = (designer.exists(column['column_alternate_id']))? column['column_alternate_id']:'';
    props['column_size'] = (designer.exists(column['column_size']))? column['column_size']:'';
    props['column_precision'] = (designer.exists(column['column_precision']))? column['column_precision']:'';
    props['column_db_encoding'] = (designer.exists(column['column_db_encoding']))? column['column_db_encoding']:'';
    props['join_type'] = (designer.exists(column['join_type']))? column['join_type']:'';
    props['other_class_name'] = (designer.exists(column['other_class_name']))? column['other_class_name']:'';
    props['other_method_name'] = (designer.exists(column['other_method_name']))? column['other_method_name']:'';
    props['enum_values'] = (designer.exists(column['enum_values']))? column['enum_values']:[];
    return props;
}
designer.collectString = function(field_name)
{
    var el=document.getElementById(field_name);
    return (el)? el.value:'';
}
designer.collectSelects= function(field_name)
{
    var el=document.getElementById(field_name);
    if(!designer.exists(el)) return '';
    if(!designer.exists(el.options)) return '';
    return (el)? el.options[el.selectedIndex].value:'';
}
designer.collectValues = function(column_type)
{
    var props = {'type':column_type};
    var fields = ['column_name','column_db_name','column_title',
                  'column_default','column_length','column_size','column_precision','column_db_encoding'];
    for(var i=0;i<fields.length;i++) { props[fields[i]] = designer.collectString(fields[i]); }
    var fields = ['column_varchar','column_unique','column_not_none','column_alternate_id'];
    for(var i=0;i<fields.length;i++) { props[fields[i]] = designer.collectSelects(fields[i]); }
    return props;
}
designer.loadBasicRows = function(props)
{
     return TBODY(null,
                  designer.tableRowInput('name','column_name',props['column_label'],nameMsg),
                  designer.tableRowInput('title','column_title',props['column_title'],titleMsg),
                  designer.tableRowInput('dbName','column_db_name',props['column_db_name'],dbNameMsg)
                  );
}
designer.isValidColumnName = function(element)
{
    if(!designer.isValidName(element.value))
    {
        element.select();
        element.focus();
        return false;
    }
    return true;
}
designer.column_types.StringCol.loadColumn = function(model_name,column_name)
{
    var lengthMsg = 'If given, type will be VARCHAR(length). If not, TEXT is assumed (i.e., lengthless).';
    var varcharMsg='If you have a length, differentiates between CHAR and VARCHAR, default True.';
    var props = designer.loadBasicValues(model_name,column_name);
    var rows = designer.loadBasicRows(props);
    rows.appendChild( designer.tableRowInput('length','column_length',props['column_length'],lengthMsg));
    rows.appendChild( designer.tableRowInput('default','column_default',props['column_default'],defaultMsg));
    rows.appendChild(designer.tableRowBool('varchar','column_varchar',props['column_varchar'],varcharMsg));
    rows.appendChild(designer.tableRowBool('unique','column_unique',props['column_unique'],uniqueMsg));
    rows.appendChild(designer.tableRowBool('notNone','column_not_none',props['column_not_none'],notnullMsg));
    rows.appendChild(designer.tableRowBool('alternateID','column_alternate_id',props['column_alternate_id'],alternateMsg));
    return rows;
}
designer.column_types.IntCol.loadColumn = function(model_name,column_name)
{
    var props = designer.loadBasicValues(model_name,column_name);
    var rows = designer.loadBasicRows(props);
    rows.appendChild(designer.tableRowInput('default','column_default',props['column_default'],defaultMsg));
    rows.appendChild(designer.tableRowBool('unique','column_unique',props['column_unique'],uniqueMsg));
    rows.appendChild(designer.tableRowBool('notNone','column_not_none',props['column_not_none'],notnullMsg));
    rows.appendChild(designer.tableRowBool('alternateID','column_alternate_id',props['column_alternate_id'],alternateMsg));
    return rows;
}
designer.column_types.DecimalCol.loadColumn = function(model_name,column_name)
{
    var props = designer.loadBasicValues(model_name,column_name);
    var rows = designer.loadBasicRows(props);
    rows.appendChild(designer.tableRowInput('size','column_size',props['column_size'],'Number of digits stored'));
    rows.appendChild(designer.tableRowInput('precision','column_precision',props['column_precision'],'Number of digits after the decimal point'));
    rows.appendChild(designer.tableRowInput('default','column_default',props['column_default'],defaultMsg));
    rows.appendChild(designer.tableRowBool('unique','column_unique',props['column_unique'],uniqueMsg));
    rows.appendChild(designer.tableRowBool('notNone','column_not_none',props['column_not_none'],notnullMsg));
    rows.appendChild(designer.tableRowBool('alternateID','column_alternate_id',props['column_alternate_id'],alternateMsg));
    return rows;
}
designer.column_types.DateCol.loadColumn = function(model_name,column_name)
{
    var props = designer.loadBasicValues(model_name,column_name);
    var rows = designer.loadBasicRows(props);
    rows.appendChild(designer.tableRowInput('default','column_default',props['column_default'],defaultMsg));
    rows.appendChild(designer.tableRowBool('unique','column_unique',props['column_unique'],uniqueMsg));
    rows.appendChild(designer.tableRowBool('notNone','column_not_none',props['column_not_none'],notnullMsg));
    rows.appendChild(designer.tableRowBool('alternateID','column_alternate_id',props['column_alternate_id'],alternateMsg));
    return rows;
}
designer.column_types.DateTimeCol.loadColumn = function(model_name,column_name)
{
    return designer.column_types.DateCol.loadColumn(model_name,column_name);
}
designer.column_types.EnumCol.loadColumn = function(model_name,column_name)
{
    var props = designer.loadBasicValues(model_name,column_name);
    var rows = designer.loadBasicRows(props);
    rows.appendChild(designer.tableRowList('values','enum_values',props['enum_values']));
    rows.appendChild(designer.tableRowDefaultSelect('default','column_default',props['enum_values'],props['column_default']));
    return rows;
}
designer.column_types.BoolCol.loadColumn = function(model_name,column_name)
{
    var props = designer.loadBasicValues(model_name,column_name);
    var rows = designer.loadBasicRows(props);
    rows.appendChild(designer.tableRowBool('default','column_default',props['column_default']));
    return rows;
}
designer.column_types.UnicodeCol.loadColumn = function(model_name,column_name)
{
    var props = designer.loadBasicValues(model_name,column_name);
    var rows = designer.column_types.StringCol.loadColumn(model_name,column_name);
    rows.appendChild(designer.tableRowInput('dbEncoding','column_db_encoding',props['column_db_encoding']));
    return rows;
}
designer.column_types.FloatCol.loadColumn = function(model_name,column_name)
{
    return designer.column_types.IntCol.loadColumn(model_name,column_name);
}
designer.column_types.CurrencyCol.loadColumn = function(model_name,column_name)
{
    return designer.column_types.IntCol.loadColumn(model_name,column_name);
}
designer.column_types.BLOBCol.loadColumn = function(model_name,column_name)
{
    var props = designer.loadBasicValues(model_name,column_name);
    return designer.loadBasicRows(props);
}
designer.column_types.PickleCol.loadColumn = function(model_name,column_name)
{
    return designer.column_types.BLOBCol.loadColumn(model_name,column_name);
}
designer.loadJoinColumn = function(model_name,column_name)
{
    var otherMNMsg = 'Name of the field on the other class that refers to this class';
    var otherCNMsg = 'Name of the class that refers to this class';
    var props = designer.loadBasicValues(model_name,column_name);
    var rows = TBODY(null,
                  designer.tableRowInput('name','column_name',props['column_label'],nameMsg),
                  designer.tableRowInput('dbName','column_db_name',props['column_db_name'],dbNameMsg)
                  );
    rows.appendChild(designer.tableRowAllClasses(props['other_class_name'],otherCNMsg));
    rows.appendChild(designer.tableRowInput('otherMethodName','other_method_name',props['other_method_name'],otherMNMsg));
    rows.appendChild( createDOM('INPUT',{'type':'hidden','value':props['other_class_name'],'id':'original_other_class_name'}));
    rows.appendChild( createDOM('INPUT',{'type':'hidden','value':props['other_method_name'],'id':'original_other_method_name'}));
    return rows;
}
designer.column_types.ForeignKey.loadColumn = function(model_name,column_name)
{
    var props = designer.loadBasicValues(model_name,column_name);
    var rows = designer.loadJoinColumn(model_name,column_name);
    rows.appendChild(designer.tableRowRelationTypes(props['join_type']));
    return rows;
}
designer.column_types.MultipleJoin.loadColumn = function(model_name,column_name)
{
    return designer.loadJoinColumn(model_name,column_name);
}
designer.column_types.SingleJoin.loadColumn = function(model_name,column_name)
{
    return designer.loadJoinColumn(model_name,column_name);
}
designer.column_types.RelatedJoin.loadColumn = function(model_name,column_name)
{
    return designer.loadJoinColumn(model_name,column_name);
}


/* ------------------------ collecting values ----------------------*/
designer.column_types.BoolCol.collectValues = function()
{
    var props = designer.collectValues('BoolCol');
    props['column_default'] = designer.collectSelects('column_default');
    return props;
}
designer.column_types.EnumCol.collectValues = function()
{
    var props = designer.collectValues('EnumCol');
    var enum_values = [];
    var ev = document.getElementById('enum_values');
    for(var i=0;i< ev.options.length;i++) { enum_values[enum_values.length] = ev.options[i].value; }
    props['enum_values'] = enum_values;
    props['column_default']=designer.collectSelects('column_default');
    return props;
}
designer.collectJoinValues = function(join_type_name)
{
    var props = designer.collectValues(join_type_name);
    props['other_class_name'] = designer.collectSelects('other_class_name');
    props['other_method_name'] = designer.collectString('other_method_name');
    props['original_other_class_name'] = designer.collectString('original_other_class_name');
    props['original_other_method_name'] = designer.collectString('original_other_method_name');

    props['join_type'] = join_type_name;

    if(!props['other_class_name'])
    {
        alert('You need to select the other class this field should refer to');
        return;
    }
    if(!designer.isValidName(props['other_method_name']))
    {
        alert('You need to correctly specify the other class field name');
        return;
    }
    return props;
}
designer.column_types.RelatedJoin.collectValues = function()
{
    return designer.collectJoinValues('RelatedJoin');
}
designer.column_types.SingleJoin.collectValues = function()
{
    return designer.collectJoinValues('SingleJoin');
}
designer.column_types.MultipleJoin.collectValues = function()
{
    return designer.collectJoinValues('MultipleJoin');
}
designer.column_types.ForeignKey.collectValues = function()
{
    var props = designer.collectJoinValues('ForeignKey');
    props['join_type'] = designer.collectSelects('join_type');

    if(!props['join_type'])
    {
        alert('You need to select the type of relationship between the two classes');
        return;
    }
    return props;
}


designer.tableRowList = function(label,name,value)
{
   var sel = createDOM('SELECT', {'size':'6','id':name});
   for(var i=0;i<value.length;i++)
   {
       sel.appendChild( createDOM('OPTION',{'value':value[i]},value[i]));
   }
   return TR(null,
                TD({'class':'label','valign':'top'},label +' :'),
                TD({'class':'field','valign':'top'},
                   createDOM('INPUT',{'type':'text','id':'enum_add'}),
                   createDOM('BUTTON',{
                                      'onclick':"designer.addEnum('"+ name +"')",
                                      'accesskey':'+',
                                      'title':'Add Enumeration value (+)',
                                      'style':'width:25px'},'+'),
                   createDOM('BUTTON',{
                                      'onclick':"designer.removeEnum('"+ name +"')",
                                      'accesskey':'-',
                                      'title':'Remove Enumeration value (-)',
                                      'style':'width:25px'},'-'),
                   createDOM('BR',null),
                   sel
                  )
           );
}
designer.addEnum = function(column_name)
{
    var el = document.getElementById(column_name);
    var newOpt = document.getElementById('enum_add');
    if(newOpt.value=='')
    {
        alert('No option to be added..');
        newOpt.focus()
        newOpt.select()
        return;
    }
    el.options[el.options.length] = new Option(newOpt.value,newOpt.value,false,false);
    newOpt.value = '';
    newOpt.focus()
    designer.updateDefaultEnum(column_name);
    designer.save();
}
designer.removeEnum = function(column_name)
{
    var el = document.getElementById(column_name);
    if(el.selectedIndex==-1)
    {
        alert('No option selected');
        var newOpt = document.getElementById('enum_add');
        newOpt.focus()
        newOpt.select()
        return;
    }

    for(var i=el.options.length-1;i >=0;i--)
    {
        if(el.options[i]!=null && el.options[i].selected) el.options[i]=null;
    }
    designer.updateDefaultEnum(column_name);
    designer.save();
}
designer.updateDefaultEnum = function(column_name)
{
    var el = document.getElementById(column_name);
    var d =document.getElementById('column_default');
    var sel = d.options[d.selectedIndex].value;

    for(var i=d.options.length-1;i>=0;i--) d.options[i] = null;
    d.options[d.length]= new Option('','',false,false);

    for(var i=0;i<el.options.length;i++)
    {
        var opt = el.options[i];
        var selected = (opt.value==sel)? true:false;
        d.options[d.length]= new Option(opt.text, opt.value, false, selected);
    }
}
designer.tableRowDefaultSelect= function(label,name,values,value)
{
   var sel = createDOM('SELECT', {'id':name});
   sel.appendChild( createDOM('OPTION',{'value':''},''));

   for(var i=0;i<values.length;i++)
   {
       var props = {'value':values[i]};
       if(values[i]==value) props['selected']='selected';
       sel.appendChild( createDOM('OPTION',props,values[i]));
   }

   return TR(null,
                TD({'class':'label','valign':'top'},label +' :'),
                TD({'class':'field'},sel)
            );
}


designer.exists = function(val)
{
  return (typeof(val) != 'undefined' && val)
}
designer.tableRowParentClass = function(label,model_name,name,value)
{
   var sel = createDOM('SELECT', {'id':name});
   var val = ['SQLObject','InheritableSQLObject','TG_User','TG_Group','TG_Permission'];

   for(var model in designer.sortedModels())
   {
        if(model==model_name) continue;
        var m = designer.models[model];
        var p = m.parent_class;
        while(designer.exists(p) &&
            designer.exists(designer.models[p]) &&
            p != model_name) p = designer.models[p].parent_class;
        if(p=='InheritableSQLObject' &&
           p != model_name) val[val.length]= m.name;
   }
   for(var i=0;i<val.length;i++)
   {
       var props = {'value':val[i]};
       if(value==val[i]) props['selected']='selected';
       sel.appendChild( createDOM('OPTION',props ,val[i] ));
   }
   return TR(null,
                TD({'class':'label'},label +' :'),
                TD({'class':'field'}, sel)
           );
}
designer.loadModelSettings = function(model_name)
{
    designer.currentModel = model_name;
    var model_name = (designer.exists(model_name))? model_name:'';
    var old_name = (model_name=='')? '__new__':model_name;
    var table_name = '';
    var id_name = '';
    var parent_class = '';
    var cancel_action = 'designer.clearCanvas()';
    if(designer.exists(model_name))
    {
        var m = designer.models[model_name];
        table_name = (designer.exists(m.table_name))? m.table_name:'';
        id_name = (designer.exists(m.id_name))? m.id_name:'';
        parent_class= (designer.exists(m.parent_class))? m.parent_class:'';
        cancel_action = "designer.loadModel('"+ model_name +"')";
    }

    var help_icon = designer.help_icon('model');
    var settings = DIV(null,
                       H1(null,help_icon,'Model Settings'),
                       TABLE({'border':'0','cellspacing':'0','cellpadding':'5'},
                         TBODY(null,
                               designer.tableRowInput('Class Name','model_name',model_name),
                               designer.tableRowParentClass('Parent Class',model_name,'parent_class',parent_class),
                               designer.tableRowInput('table','table_name',table_name),
                               designer.tableRowInput('idName','id_name',id_name),
                               TR(null,
                                    TD({'colspan':'2','align':'right','class':'action_row'},
                                       createDOM('INPUT',{'type':'hidden','value':old_name,'id':'old_name'}),
                                       designer.button(cancel_action,'c',
                                                        'Cancel (c)',
                                                        SPAN(null,createDOM('U',null,'C'),'ancel')),
                                       designer.button('designer.saveModelSettings()','s',
                                                        'Save settings (s)',
                                                        SPAN(null,createDOM('U',null,'S'),'ave'))
                                    )
                               )

                          )
                       )
                    );

    replaceChildNodes('canvas',settings);
    document.getElementById('model_name').select();
    document.getElementById('model_name').focus();
}
designer.isValidName = function(model_name)
{
    if(!designer.exists(model_name))
    {
        alert('Name missing');
        return false;
    }
    if(model_name.indexOf(' ') != -1)
    {
        alert('The name can not contain spaces');
        return false;
    }

    return true;
}
designer.saveModelSettings = function()
{
    var new_name = document.getElementById('model_name');
    var old_name = document.getElementById('old_name');
    if(!designer.isValidName(new_name.value))
    {
        new_name.select();
        new_name.focus();
        return;
    }

    var parent_class  = document.getElementById('parent_class');
    parent_class = parent_class.options[parent_class.selectedIndex].value;
    var props ={
                   'name':new_name.value,
                   'parent_class':parent_class,
                   'table_name':document.getElementById('table_name').value,
                   'id_name':document.getElementById('id_name').value,
                   'columns':{},
                   'relations':{}
               }

    if(old_name.value !='__new__')
    {
        var old_props = designer.models[old_name.value];
        delete designer.models[old_name.value];
        props['columns'] = old_props.columns;
        props['relations'] = old_props.relations;
    }
    designer.models[new_name.value]= props;
    designer.loadModels();
    designer.loadModel(new_name.value);
    designer.save();
}
designer.sortedModels = function()
{
    if(!designer.exists(designer.ordered_models)) return designer.models;
    var modelsCopy = {};
    var reordered = {};
    for(var m in designer.models) modelsCopy[m]=true;
    for(var i=0;i < designer.ordered_models.length;i++)
    {
        var m_name = designer.ordered_models[i];
        if(designer.exists(modelsCopy[m_name]))
        {
            delete modelsCopy[m_name];
            reordered[m_name]= true;
        }
    }
    for(var m in modelsCopy) reordered[m]= true;
    return reordered;
}

designer.loadModels = function()
{
  var models = UL({'id':'object_list'});
  for(var model in designer.sortedModels())
  {
    var model_link = TD(null,A({'href':"javascript:designer.loadModel('"+ model +"')",'class':'action'},model));
    var handle = TD({'id':'handle_'+ model,'class':'handle'},'\u2195');
    var m_over ='if(document.getElementById("handle_'+ model +'")) ';
    m_over+='document.getElementById("handle_'+ model +'").style.visibility="visible"';
    var m_out = 'if(document.getElementById("handle_'+ model +'")) ';
    m_out+='document.getElementById("handle_'+ model +'").style.visibility="hidden"';

    models.appendChild(
                        LI({'itemID':model,'onmouseover':m_over,'onmouseout':m_out},
                           TABLE({'border':'0','cellspacing':'2'}, TBODY(null, TR(null, handle, model_link) ) )
                        )
                       );
  }
  replaceChildNodes('models',models);
  dragsort.makeListSortable(document.getElementById('object_list'),setHandle,designer.endModelDrag)
}
designer.endModelDrag = function(item)
{
  var group = item.toolManDragGroup
  var list = group.element.parentNode
  var id = list.getAttribute("id")
  if (id == null) return;
  group.register('dragend', function() { designer.saveModelOrder(junkdrawer.serializeList(list)) });
}
designer.saveModelOrder = function(list)
{
    designer['ordered_models'] = list.split('|');
    designer.save();
}
designer.loadModel = function(model_name)
{
    designer.minimazeCanvas();
    designer.currentModel = model_name;
    var preview = DIV(null,
                      H1(null,model_name, SPAN({'class':'parent_class'},' : ',designer.models[model_name].parent_class) ),
                      designer.columnList(model_name),
                      DIV({'id':'model_actions'},
                           designer.button("designer.deleteModel('"+ model_name +"')",'d',
                                            'Delete Model (d)',
                                            SPAN(null,createDOM('U',null,'D') ,'elete')),
                           designer.button("designer.loadModelSettings('"+ model_name +"')",'e',
                                            'Edit Model (e)',
                                            SPAN(null,createDOM('U',null,'E') ,'dit'))
                         )
                    );

    replaceChildNodes('canvas',preview);
    document.getElementById('column_types').focus();
    dragsort.makeListSortable(document.getElementById('ul_columns_list'),setHandle,designer.endColumnDrag)
}
designer.columnList = function(model_name)
{
    var add_field = designer.button("designer.addColumn('"+ model_name +"')",'f','Add Field (f)',
                                    SPAN(null,'Add ',createDOM('U',null,'F'),'ield'));
    var help_icon = TD({'style':'background-color:#fff'}, designer.help_icon('column_type_list'));
    var columns = DIV({'class':'columns_list'},
                      designer.modelColumns(model_name),
                      TABLE({'border':'0','cellmargin':'0','cellpadding':'4','class':'add_column'},
                            TBODY(null, TR(null, TD(null,designer.columnTypeList()), TD({'align':'right'},add_field),help_icon ) ) )
                  );
    return columns;
}
designer.endColumnDrag = function(item)
{
  var group = item.toolManDragGroup
  var list = group.element.parentNode
  var id = list.getAttribute("id")
  if (id == null) return;
  group.register('dragend', function() { designer.saveColumnOrder(junkdrawer.serializeList(list)) });
}
designer.saveColumnOrder = function(list)
{
    if(!designer.exists(designer.currentModel)) return;
    designer.models[designer.currentModel]['ordered_columns'] = list.split('|');
    designer.save();
}
designer.show_help = function(context)
{
    if(context=='column_type_list')
    {
        var a = document.getElementById('column_types');
        context = a.options[a.selectedIndex].value;
    }
    var topicName =  context+'__doc__';
    var doc = document.getElementById(topicName);
    var help = document.getElementById('help');
    var help_content = document.getElementById('help_content');
    help_content.innerHTML = doc.innerHTML;
    help.style.visibility = 'visible';
}
designer.hide_help = function()
{
    var help = document.getElementById('help');
    help.style.visibility = 'hidden';
}
designer.sortedColumn = function(model_name)
{
    var model = designer.models[model_name];
    if(!designer.exists(model.ordered_columns)) return model.columns;
    var columnsCopy = {};
    var reordered = {};
    for(var m in model.columns) columnsCopy[m]=true;
    for(var i=0;i < model.ordered_columns.length;i++)
    {
        var c_name = model.ordered_columns[i];
        if(designer.exists(columnsCopy[c_name]))
        {
            delete columnsCopy[c_name];
            reordered[c_name]= true;
        }
    }
    for(var m in columnsCopy) reordered[m]= true;
    return reordered;
}
designer.modelColumns = function(model_name)
{
    var columns = UL({'id':'ul_columns_list','class':'boxy','style':'width:400px'});
    var c = designer.models[model_name].columns
    for(var column in designer.sortedColumn(model_name))
    {
       var action= A({'class':'action',
                      'href':"javascript:designer.editColumn('"+ model_name +"','"+ c[column]['type'] +"','"+ column +"')"},
                       column
                    );

       var m_over ='if(document.getElementById("handle_'+ column +'")) ';
       m_over+='document.getElementById("handle_'+ column +'").style.visibility="visible"';
       var m_out = 'if(document.getElementById("handle_'+ column +'")) ';
       m_out+='document.getElementById("handle_'+ column +'").style.visibility="hidden"';

       var column_type = c[column]['type'];
       if(designer.isJoin(column_type)) column_type += ':'+ c[column]['other_class_name'] +'.'+ c[column]['other_method_name'];
       columns.appendChild(
                            LI({'itemID':column,'onmouseover':m_over,'onmouseout':m_out},
                               TABLE({'border':'0','cellspacing':'0','cellpadding':'5','width':'100%'},
                                     TBODY(null,
                                         TR(null,
                                            TD({'id':'handle_'+ column ,'class':'handle'},'\u2195'),
                                            TD({'style':'width:120px'},action),
                                            TD({'class':'faded','style':'width:120px'},c[column]['title']),
                                            TD({'class':'faded','nowrap':'nowrap'},column_type),
                                            TD({'align':'right'},
                                               A({'href':"javascript:designer.deleteColumn('"+ model_name +"','"+ column +"')",
                                                  'title':'Delete column','class':'delete'},
                                                 'Delete'
                                              )
                                            )
                                         )
                                     )
                                )
                            )
                          );
    }
    return columns
}
designer.deletingColumn = function(model_name,column_name)
{
    var column = designer.models[model_name].columns[column_name];
    if(designer.isJoin(column['type'])) //delete any joins for this column
    {
        var other_class_name = column['other_class_name'];
        var other_method_name = column['other_method_name'];
        if(designer.exists(designer.models[other_class_name]))
        {
            if(designer.exists(designer.models[other_class_name].columns[other_method_name]))
            {
                delete designer.models[other_class_name].columns[other_method_name];
            }
        }
    }
    delete designer.models[model_name].columns[column_name];
    designer.save();
}
designer.deleteColumn = function(model_name,column_name)
{
    if(!confirm('Are you shure you want to delete '+ column_name +'?')) return;
    designer.deletingColumn(model_name,column_name);
    designer.loadModel(model_name);
}
designer.deleteModel = function(model_name)
{
    if(!confirm('Are you shure you want to delete '+ model_name +'?')) return;

    var c = designer.models[model_name].columns
    for(var column in c) designer.deletingColumn(model_name,column);
    delete designer.models[model_name];
    replaceChildNodes('canvas','');
    designer.loadModels();
    designer.save();
}
designer.clearCanvas = function()
{
    replaceChildNodes('canvas','');
}
designer.columnTypeList = function()
{
  var column_types = createDOM('SELECT', {'id':'column_types'});
  for(var column_type in designer.column_types)
  {
    column_types.appendChild(
                              createDOM('OPTION', {'value':column_type}, column_type )
                            );
  }
  return column_types;
}
designer.addColumn = function(model_name)
{
    var column_type = document.getElementById('column_types');
    column_type = column_type.options[column_type.selectedIndex].value;

    var column = designer.loadColumn(model_name,column_type,'__new__');
    replaceChildNodes('canvas',column);

    document.getElementById('column_name').select();
    document.getElementById('column_name').focus();
    designer.save();
}
designer.editColumn = function(model_name,column_type,column_name)
{
    var column = designer.loadColumn(model_name,column_type,column_name);
    replaceChildNodes('canvas',column);

    document.getElementById('column_name').select();
    document.getElementById('column_name').focus();
}
designer.button = function(action,accesskey,title,label)
{
    return createDOM('BUTTON',
                     {
                      'onclick':action,
                      'accesskey':accesskey,
                      'title':title,
                      'style':'font-size:10px'
                     },label
                   );
}
designer.help_icon = function(context)
{
    return '';
    return A({'id':'help_icon',
            'onmouseout':'designer.hide_help()',
            'onmouseover':"designer.show_help('"+ context +"')",
            'href':'#'},
            IMG({'src':'/tg_toolbox/designer/images/info.png','border':'0','align':'right'})
           );
}
designer.loadColumn = function(model_name,column_type,column_name)
{
    designer.currentModel = model_name;
    var column_label = (column_name=='__new__')? 'New '+ column_type:column_name;
    var help_icon = designer.help_icon(column_type);
    var columnTable = TABLE({'border':'0','cellspacing':'0','cellpadding':'5'},
                             designer.column_types[column_type].loadColumn(model_name,column_name)
                           );

    var column = DIV(null,
                    H1(null,help_icon, column_label, SPAN({'class':'parent_class'},' : ',model_name) ),
                    columnTable,
                    DIV(null,
                        designer.button("designer.loadModel('"+ model_name +"')",'c',
                                        'Cancel (c)',
                                        SPAN(null,createDOM('U',null,'C'),'ancel')
                                      ),
                        designer.button("designer.saveColumn('"+ column_type +"','"+ model_name +"','"+ column_name +"')",'s',
                                        'Save (s)',
                                        SPAN(null,createDOM('U',null,'S'),'ave')
                                      )
                        )
                );
    return column;
}
designer.referredClassHasChanged = function(orig_other_class_name,other_class_name)
{
    if(orig_other_class_name =='') return false;
    if(orig_other_class_name != other_class_name) return true;
    return false;
}
designer.referredMethodHasChanged = function(orig_other_method_name,other_method_name)
{
    if(orig_other_method_name =='') return false;
    if(orig_other_method_name != other_method_name) return true;
    return false;
}
designer.updateOpositeRelationSide = function(model_name,props)
{
    var orig_other_class_name = props['original_other_class_name'];
    var orig_other_method_name = props['original_other_method_name'];

    var other_class_name = props['other_class_name'];
    var other_method_name = props['other_method_name'];

    //are whe refering to a new class? delete the method on the old class then
    if(designer.referredClassHasChanged(orig_other_class_name, other_class_name) )
    {
        delete designer.models[orig_other_class_name].columns[orig_other_method_name];
    }

    //has the method name been updated, if so copy the old method properties?
    if(designer.referredMethodHasChanged(orig_other_method_name,other_method_name))
    {
        //alert('orig_other_class_name:'+ orig_other_class_name +',orig_other_method_name:'+ orig_other_method_name);
        var props = designer.models[orig_other_class_name].columns[orig_other_method_name];
        props['column_name'] = other_method_name;
        props['column_label'] = other_method_name;
        designer.models[orig_other_class_name].columns[other_method_name] = props;
        delete designer.models[orig_other_class_name].columns[orig_other_method_name];
    }

    if(!designer.exists(designer.models[other_class_name].columns[other_method_name]))
    {
        designer.models[other_class_name].columns[other_method_name]= {'type':'ForeignKey'};
        if(props['type']=='ForeignKey' || props['type']=='RelatedJoin')
        {
            designer.models[other_class_name].columns[other_method_name]['type']=props['join_type'];
        }
    }

    designer.models[other_class_name].columns[other_method_name]['column_name']= props['other_method_name'];
    designer.models[other_class_name].columns[other_method_name]['join_type']= props['join_type'];
    designer.models[other_class_name].columns[other_method_name]['other_class_name']= model_name;
    designer.models[other_class_name].columns[other_method_name]['other_method_name']= props['column_name'];
    designer.save();
}
designer.saveColumn = function(column_type,model_name,column_name)
{
    if(!designer.isValidColumnName(document.getElementById('column_name'))) return;
    if(designer.exists(designer.column_types[column_type].collectValues))
    {
        var column_values = designer.column_types[column_type].collectValues();
    }
    else
    {
        var column_values = designer.collectValues(column_type);
    }
    if(!column_values) return;
    if(designer.exists(designer.models[model_name].columns[column_name]))
    {
        delete designer.models[model_name].columns[column_name];
    }
    if(designer.isJoin(column_type)) designer.updateOpositeRelationSide(model_name,column_values);
    designer.models[model_name].columns[column_values['column_name']]= column_values;
    designer.loadModel(model_name);
    designer.save();
}
designer.isDate= function(column_type)
{
    if(column_type=='DateCol') return true;
    if(column_type=='DateTimeCol') return true;
    return false;
}
designer.isNumeric = function(column_type)
{
    if(column_type=='IntCol') return true;
    if(column_type=='FloatCol') return true;
    if(column_type=='DecimalCol') return true;
    if(column_type=='CurrencyCol') return true;
    return false;
}
designer.isJoin = function(column_type)
{
    if(column_type=='RelatedJoin') return true;
    if(column_type=='SingleJoin') return true;
    if(column_type=='MultipleJoin') return true;
    if(column_type=='ForeignKey') return true;
    return false;
}
designer.saveModel = function()
{
   var session = {};
   session['name'] = 'survey';
   session['models'] = designer.models;
   session['ordered_models'] = designer.ordered_models;

   var serializedModel =serializeJSON(session);
   document.getElementById('output').value=serializedModel;
   alert('Saved');
}
designer.loadCurrentModel = function(result)
{
    var session = result['model'];
    designer.models = session['models'];
    designer.ordered_models = session['ordered_models'];
    designer.loadModels();
    designer.minimazeCanvas();
    replaceChildNodes('canvas','');
}
designer.retrieveCurrentModel = function()
{
    var d = postJSONDoc('load_current_model','');
    d.addCallback(designer.loadCurrentModel);
}
designer.loadSampleModel = function()
{
    var el = document.getElementById('sample_models');
    var model_name = el.options[el.selectedIndex].value;

    if(model_name=='none')
    {
        alert('Choose a model from the list');
        return;
    }
    if(model_name=='model_designer_session_file')
    {
        designer.retrieveSession();
        return;
    }
    var d = postJSONDoc('retrieve_sample','name='+ model_name);
    d.addCallback(designer.loadSession);
}
designer.retrieveSession = function()
{
    var d = postJSONDoc('current_session_model','');
    d.addCallback(designer.loadSession);
}
designer.saveCurrentSession = function()
{
    var session_name = prompt('Session Name','');
    if(!session_name) return;
    designer.save(session_name);
}
designer.loadSession = function(result)
{
    var session = evalJSON(result['session']);
    designer.models = session['models'];
    designer.ordered_models = session['ordered_models'];
    designer.loadModels();
    designer.minimazeCanvas();
    replaceChildNodes('canvas','');
}
designer.foreignKeyCode = function(column,p)
{
    if(p!='')p+=',';
    p+='"'+ column['other_class_name'] +'"';
    if( (column['type']=='MultipleJoin' || column['type']=='SingleJoin')
        && designer.exists(column['other_method_name']) )
    {
        p+=",joinColumn='"+ column['other_method_name'].toLowerCase() +"_id'";
    }
    return p;
}
designer.stringCode = function(column,p)
{
    if(designer.exists(column['column_length']))
    {
        if(p!='')p+=',';
        p+='length='+ column['column_length'];
    }
    if(designer.exists(column['column_varchar']))
    {
        if(p!='')p+=',';
        p+='varchar='+ column['column_varchar'];
    }
    return p;
}
designer.unicodeCode = function(column,p)
{
    if(designer.exists(column['column_db_encoding']))
    {
        if(p!='')p+=',';
        p+='dbEncoding="'+ column['column_db_encoding']+'"';
    }
    return p;
}
designer.decimalCode = function(column,p)
{
    if(designer.exists(column['column_size']))
    {
        if(p!='')p+=',';
        p+='size='+ column['column_size'];
    }
    if(designer.exists(column['column_precision']))
    {
        if(p!='')p+=',';
        p+='precision='+ column['column_precision'];
    }
    return p;
}
designer.enumCode = function(column,p)
{
    var enum_values='';
    for(var i=0;i < column['enum_values'].length;i++)
    {
        if(enum_values!='') enum_values+=',';
        enum_values+="'"+ column['enum_values'][i] +"'";
    }

    if(p!='')p+=',';
    p+='enumValues=['+ enum_values +']';
    return p;
}
designer.columnCode = function(model_name,columns)
{
    var col_string = '';
    for(var c in designer.sortedColumn(model_name))
    {
       var column = columns[c];
       col_string+= designer.indent(1) + c +' = ';
       col_string+= column['type'] +'(';
       var p = '';
       //general default is missing...
       switch(column['type'])
       {
          case('StringCol'):
            p = designer.stringCode(column,p);
            break;
          case('EnumCol'):
            p = designer.enumCode(column,p);
            break;
          case('DecimalCol'):
            p = designer.decimalCode(column,p);
            break;
          case('ForeignKey'):
            p = designer.foreignKeyCode(column,p);
            break;
          case('MultipleJoin'):
            p = designer.foreignKeyCode(column,p);
            break;
          case('SingleJoin'):
            p = designer.foreignKeyCode(column,p);
            break;
          case('RelatedJoin'):
            p = designer.foreignKeyCode(column,p);
            break;
          //decimal
          //enum
       }
       if(designer.exists(column['column_title']))
       {
           if(p!='')p+=',';
           p+='title="'+ column['column_title'] +'"';
       }
       if(designer.exists(column['column_db_name']))
       {
           if(p!='')p+=',';
           p+='dbName="'+ column['column_db_name'] +'"';
       }
       if(designer.exists(column['column_alternate_id']))
       {
           if(p!='')p+=',';
           p+='alternateID='+ column['column_alternate_id'];
       }
       if(designer.exists(column['column_default']))
       {
           if(p!='')p+=',';
           var d = column['column_default'].toLowerCase();
           var quoted = true;
           if(column['column_default'].indexOf('None')!=-1) quoted = false;
           if(designer.isDate(column['type']))
           {
              if(d.indexOf('now')!=-1) quoted = false;
           }
           if(designer.isNumeric(column['type'])) quoted = false;
           if(d.indexOf('(') !=-1) quoted = false;
           p+='default=';
           p+= (quoted)?'"'+ column['column_default'] +'"': column['column_default'];
       }
       if(designer.exists(column['column_unique']))
       {
           if(p!='')p+=',';
           p+='unique='+ column['column_unique'];
       }
       if(designer.exists(column['column_not_none']))
       {
           if(p!='')p+=',';
           p+='notNone='+ column['column_not_none'];
       }

       col_string+=p;
       col_string+=')';
       col_string+='\n'
    }
    return col_string;
}
designer.indent = function(n)
{
    var s = '';
    for(var i=0;i<n;i++) s+='    ';
    return s;
}
designer.sqlmetaCode = function(model)
{
    var m = '';
    if(designer.exists(model['table_name'])) m+= designer.indent(2) + "table ='"+ model['table_name'] +"'"+ '\n';
    if(designer.exists(model['id_name'])) m+=designer.indent(2)+ "idName ='"+ model['id_name'] +"'"+ '\n';
    if(m !='') m = designer.indent(1)+'class sqlmeta:\n'+ m;
    return m;
}
designer.modelCode = function(model)
{
    var model_string = designer.sqlmetaCode(model);
    model_string += designer.columnCode(model['name'],model['columns']);
    if (!model_string) model_string = designer.indent(1) + 'pass\n';
    model_string = 'class '+ model['name'] +'('+ model['parent_class'] +'):\n' + model_string + '\n\n';
    return model_string;
}
designer.settingsView = function()
{
    designer.minimazeCanvas();
    if(designer.exists(designer.currentModel) &&
       designer.exists(designer.models[designer.currentModel]) )
    {
        designer.loadModel(designer.currentModel);
    }
    else
    {
        designer.loadModelSettings();
    }
}
designer.minimazeCanvas = function()
{
  //document.getElementById('help').style.width='250px';
  if(window.frames['diagram'])
  {
    window.frames['diagram'].document.location.href='about:blank';
  }
  document.getElementById('diagram').style.display='none';
}
designer.maximazeCanvas = function()
{
  //document.getElementById('help').style.width='0px';
  return;
}
designer.diagramView = function()
{
  designer.maximazeCanvas();
  var ifr = document.getElementById('diagram');
  ifr.style.display='block';
  ifr.style.height='800px';
  var fr = window.frames;
  var dia = window.frames['diagram'];
  dia.document.location.href='/tg_toolbox/designer/diagram/index.html';
  replaceChildNodes('canvas','');
}
designer.loadDiagram = function(doc)
{
    var f = window.frames['diagram'];
    var relations = [];
    var indexedModels = {};
    var indexedColumns = {};

    var idx = 0;
    var models = designer.sortedModels();
    for(var model in models)
    {
      var m = designer.models[model];
      m['idx'] = idx;

      var col_idx = 1;
      var columns = designer.sortedColumn(m.name);
      for(var column in columns)
      {
        n = model+'_'+column;
        column_type = designer.models[model].columns[column]['type'];
        indexedColumns[n] = col_idx;
        col_idx++;
      }

      indexedModels[model] = m;
      idx++;
    }

    idx=0;
    for(var model in models)
    {
      var m = designer.models[model];
      f.add_table(0,0,m.name);
      f.table_array[idx].addRow('id',0);
      var columns = designer.sortedColumn(m.name);
      var col_idx = 1;
      for(var column in columns)
      {
        var c= designer.models[model].columns[column];
        var column_type = c['type'];
        var column_label = column +' ['+ column_type;

        if(designer.isJoin(column_type))
        {
            var idx_m = indexedModels[c['other_class_name']];
            var col = 0;
            column_label+= ':'+ c['other_class_name']+'.'+ c['other_method_name'];
            if(designer.exists(c['other_method_name']))
            {
                n = idx_m.name +'_'+ c['other_method_name'];
                col = indexedColumns[n];
            }
            relations[relations.length] = [idx,col_idx,idx_m['idx'],col];
        }
        column_label+=']';
        f.table_array[idx].addRow(column_label,4);
        col_idx++;
      }
      idx++;
    }
    for(var i=0;i< relations.length;i++)
    {
        t1 = relations[i][0];
        r1 = relations[i][1];
        t2 = relations[i][2];
        r2 = relations[i][3];
        if(t1<t2)
        {
            t3 = t1;
            t1 = t2;
            t2 = t3;
            r3 = r1;
            r1 = r2;
            r2 = r3;
        }
        f.add_relation(t1,r1,t2,r2);
    }

    if(idx > 0)
    {
        f.raise_table(0);
        f.reposition_tables();
    }
}
designer.code_saved = function(result)
{
    alert(result['status']);
}
designer.save_code_and_create_tables = function()
{
    var code = document.getElementById('code_view').value;
    ordered_models = '';

    for(var model in designer.sortedModels())
    {
        if(ordered_models!='') ordered_models+=',';
        ordered_models+= designer.models[model].name;
    }
    var d = postJSONDoc('save_and_create','code='+ code +'&order='+ ordered_models);
    d.addCallback(designer.code_saved);
}
designer.save_generated_code = function()
{
    var code = document.getElementById('code_view').value;
    var d = postJSONDoc('save','code='+ code);
    d.addCallback(designer.code_saved);
}
designer.save = function(save_as)
{
    var name = document.myform.model_name.value;
    if(name=='None' || name == '') return;
    var d = {'name':name,'models':designer.models,'ordered_models':designer.ordered_models };
    var state = serializeJSON(d);
    var params = 'state='+ state;
    if( designer.exists(save_as) ) params+='&name='+ save_as
    var d = postJSONDoc('save_state',params);
    if( designer.exists(save_as) ) d.addCallback(designer.state_saved);
}
designer.loadSessionList = function()
{
    var d = postJSONDoc('session_list','');
    d.addCallback(designer.renderSessionList);
}
designer.renderSessionList = function(result)
{
    if(!designer.exists(result['models'])) return;

    var el = document.getElementById('sample_models');
    var tmp_file_exists = (el.options[1].value == 'model_designer_session_file')? true:false;
    for(var i=el.options.length-1;i>=0;i--) el.options[i] = null;

    el.options[0]= new Option('Sample models','none',false,false);
    if(tmp_file_exists) el.options[1]= new Option('Existing Designer Session','model_designer_session_file',false,true);

    for(var i=0;i< result['models'].length;i++)
    {
        el.options[el.length]= new Option(result['models'][i], result['models'][i], false, false);
    }
}
designer.state_saved = function(result)
{
   if(result['state'])
   {
    alert('Your Session has been saved');
    designer.loadSessionList();
   }
   else
   {
    alert('Fail to save your Session');
   }
}
function postJSONDoc(url,postVars)
{
  var req = getXMLHttpRequest();
  req.open('POST',url,true);
  req.setRequestHeader('Content-type','application/x-www-form-urlencoded');
  var data = postVars;
  var d = sendXMLHttpRequest(req,data);
  return d.addCallback(evalJSONRequest);
}
designer.codeView = function()
{
    designer.minimazeCanvas();
    var code = '';
    for(var model in designer.sortedModels())
    {
        code+= designer.modelCode(designer.models[model]);
    }

    var code_view = createDOM('TEXTAREA', {'id':'code_view','class':'py','name':'code'});

    if(document.myform.model_exists.value=='1')
    {
        var write_model = createDOM('BUTTON',
                                        {
                                          'onclick':"designer.save_generated_code()",
                                          'title':'Write to model file',
                                          'style':'cursor:pointer;font-size:10px;width:160px'
                                         },'Write model file'
                                       );
        var generate_model = createDOM('BUTTON',
                                        {
                                          'onclick':"designer.save_code_and_create_tables()",
                                          'title':'Write to model file and create tables',
                                          'style':'cursor:pointer;font-size:10px;width:200px'
                                         },'Write to file and Create Tables'
                                       );
        //generate_model = '';
        code_view = DIV({'margin-bottom':'50px'}, write_model, generate_model, code_view );
    }
    replaceChildNodes('canvas',code_view);
    var element = document.getElementById('code_view');
    element.value = code;

    // instantiate a brush
	var highlighter = null;
	var registered = new Object();
	var propertyName = 'value';
	for(var brush in dp.sh.Brushes)
	{
		var aliases = dp.sh.Brushes[brush].Aliases;
		if(aliases == null) continue;
		for(var i = 0; i < aliases.length; i++) registered[aliases[i]] = brush;
	}

    var highlighter = new dp.sh.Brushes[registered['py']]();
    element.style.display = 'none';

    highlighter.addGutter = true;
    highlighter.addControls = true;
    highlighter.firstLine = 1;
    highlighter.Highlight(element[propertyName]);
    var div = document.createElement('DIV');
    div.className = 'dp-highlighter';
    div.appendChild(highlighter.ol);
    element.parentNode.insertBefore(div, element);
}
function blankSlate()
{
    designer.currentModel='';
    designer.models = {};
    designer.ordered_models=[];

    replaceChildNodes('models','');
    replaceChildNodes('canvas','');
}
var dragsort = ToolMan.dragsort()
var junkdrawer = ToolMan.junkdrawer()

function endModelDrag(item)
{
  var group = item.toolManDragGroup
  var list = group.element.parentNode
  var id = list.getAttribute("id")
  if (id == null) return;
  group.register('dragend', function() { saveModelOrder(junkdrawer.serializeList(list)) });
}
function saveModelOrder(list)
{
    alert(list);
}

function setHandle(item) { item.toolManDragGroup.setHandle(findHandle(item) ); }
function findHandle(item)
{
  var children = item.getElementsByTagName("td");
  for (var i = 0; i < children.length; i++)
  {
    var child = children[i]
    if (child.getAttribute("class") == null) continue
    if (child.getAttribute("class").indexOf("handle") >= 0) return child
  }
  return item;
}
