var cat_browse = {};
cat_browse.highlight = function(element,state,original_color)
{
    if(state)
    { 
        element.style.backgroundColor = '#e3e3e3'; 
        document.getElementById(element.id +'_edit').style.visibility = 'visible';
        document.getElementById(element.id +'_delete').style.visibility = 'visible';
    }
    else 
    { 
        element.style.backgroundColor = original_color; 
        document.getElementById(element.id +'_edit').style.visibility = 'hidden';
        document.getElementById(element.id +'_delete').style.visibility = 'hidden';
    }
}
cat_browse.next_page= function(object_name,start,page_size)
{
    var start = parseInt(start) + parseInt(page_size);
    catwalk.browse(object_name,start,page_size);
}
cat_browse.previous_page= function(object_name,start,page_size)
{
    var start = parseInt(start) - parseInt(page_size);
    if(start < 0) start=0;
    catwalk.browse(object_name,start,page_size);
}
cat_browse.update_page_size= function(object_name,list,start)
{ 
    var page_size = list.options[list.selectedIndex].value;
    catwalk.browse(object_name,start,page_size);
}
cat_browse.update_page= function(object_name,list,page_size)
{
    var start = list.options[list.selectedIndex].value;
    catwalk.browse(object_name,start,page_size);
}
cat_browse.manage_columns = function(object_name,start,page_size)
{
  cat_browse['start'] = start;
  cat_browse['page_size'] = page_size;
  cat_browse['object_name'] = object_name;
  GB_show('Column Management','browse/columns?object_name='+ object_name, 500, 700);
  //cat_browse.management_window();
}
cat_browse.management_window = function()
{
  var my_overlay = document.getElementById('GB_overlay');
  var my_window = document.getElementById('GB_window');
  my_overlay.style.display='block';
  my_window.style.display='block';
  my_window.style.width = '500px';

  var array_page_size = GB_getWindowSize();
  my_overlay.style.width = array_page_size[0]+ 'px'; 
  var max_height = Math.max(getScrollTop()+array_page_size[1], getScrollTop()+GB_HEIGHT+30);
  my_overlay.style.height = max_height + "px";
    
}
cat_browse.columns_saved= function(object_name,context)
{
    GB_hide();
    cat_browse['object_name'] = object_name;
    setTimeout("cat_browse.reload()",500);
}
cat_browse.reload = function()
{
    catwalk.browse(cat_browse['object_name'],cat_browse['start'],cat_browse['page_size']); 
}
cat_browse.selecting = function(object_name,id)
{
    catwalk.retrieveDisplayObject(object_name,id);
}
cat_browse.deleting = function(object_name,id)
{
    catwalk.retrieveRemove(object_name,id);
}
cat_browse.editing = function(object_name,id)
{
    catwalk.retrieveFormEdit(object_name,id);
}
cat_browse.adding = function(object_name)
{
    catwalk.retrieveFormAdd(object_name);
}
