"""The bigger TurboGears widgets"""

__all__ = ['CalendarDatePicker', 'CalendarDateTimePicker',
    'AutoCompleteField', 'AutoCompleteTextField',
    'LinkRemoteFunction', 'RemoteForm', 'AjaxGrid', 'URLLink']

import itertools
from datetime import datetime

from turbogears import validators, expose
from turbojson import jsonify
from turbogears.widgets.base import (CSSLink, JSLink, CSSSource, JSSource,
    Widget, WidgetsList, static, mochikit, CoreWD)
from turbogears.widgets.i18n import CalendarLangFileLink
from turbogears.widgets.forms import (FormField, CompoundFormField, TextField,
    HiddenField, TableForm, CheckBox, RadioButtonList)
from turbogears.widgets.rpc import RPC


class CalendarDatePicker(FormField):
    """Use a Javascript calendar system to allow picking of calendar dates."""

    template = """
    <span xmlns:py="http://genshi.edgewall.org/" class="${field_class}">
    <input type="text" id="${field_id}" class="${field_class}" name="${name}" value="${strdate}" py:attrs="attrs"/>
    <input type="button" id="${field_id}_trigger" class="date_field_button" value="${button_text}"/>
    <script type="text/javascript">
    Calendar.setup({
        inputField: '${field_id}',
        ifFormat: '${format}',
        button: '${field_id}_trigger'
        <span py:if="picker_shows_time" py:replace="', showsTime : true'"/>
    });
    </script>
    </span>
    """
    params = ['attrs', 'skin', 'picker_shows_time', 'button_text',
        'format', 'calendar_lang']
    params_doc = {
        'attrs': 'Extra attributes',
        'skin': 'For alternate skins, such as "calendar-blue" or "skins/aqua/theme"',
        'picker_shows_time': 'Whether the calendar should let you pick a time, too',
        'button_text': 'Text for the button that will show the calendar picker',
        'format': 'The date format (default is mm/dd/yyyy)',
        'calendar_lang': 'The language to be used in the calendar picker.'
    }
    attrs = {}
    skin = 'calendar-system'
    picker_shows_time = False
    button_text = 'Choose'
    format = '%m/%d/%Y'
    calendar_lang = None
    _default = None

    def __init__(self, name=None, default=None, not_empty=True,
            calendar_lang=None, validator=None, format=None, **kw):
        super(CalendarDatePicker, self).__init__(name, **kw)
        self.not_empty = not_empty
        if default is not None or not self.not_empty:
            self._default = default
        if format is not None:
            self.format = format
        if validator is None:
            self.validator = validators.DateTimeConverter(
                format=self.format, not_empty=self.not_empty)
        else:
            self.validator = validator
        if calendar_lang:
            self.calendar_lang = calendar_lang
        javascript = [JSLink(static, 'calendar/calendar.js'),
            JSLink(static, 'calendar/calendar-setup.js')]
        javascript.append(CalendarLangFileLink(static,
            language=self.calendar_lang))
        self.javascript = self.javascript + javascript
        if self.skin:
            css = [CSSLink(static, 'calendar/%s.css' % self.skin)]
            self.css = self.css + css

    @property
    def default(self):
        if self._default is None and self.not_empty:
            return datetime.now()
        return self._default

    def update_params(self, d):
        super(CalendarDatePicker, self).update_params(d)
        if hasattr(d['value'], 'strftime'):
            d['strdate'] = d['value'].strftime(d['format'])
        else:
            d['strdate'] = d['value']


class CalendarDatePickerDesc(CoreWD):

    name = "Calendar"
    for_widget = CalendarDatePicker('date_picker')


class CalendarDateTimePicker(CalendarDatePicker):
    """Javascript calendar system to allow picking of dates with times."""

    format = '%Y/%m/%d %H:%M'
    picker_shows_time = True


class CalendarDateTimePickerDesc(CoreWD):

    name = "Calendar with time"
    for_widget = CalendarDateTimePicker("datetime_picker")


class AutoComplete(Widget):
    """Mixin class for autocomplete fields.

    Performs Ajax-style autocompletion by requesting search
    results from the server as the user types.

    """

    javascript = [mochikit, JSLink(static,"autocompletefield.js")]
    css = [CSSLink(static,"autocompletefield.css")]
    params = ['search_controller', 'search_param', 'result_name', 'attrs',
        'only_suggest', 'complete_delay', 'take_focus', 'min_chars', 'show_spinner']
    params_doc = {
        'attrs': 'Extra attributes',
        'search_controller': 'Name of the controller returning the auto completions',
        'search_param': 'Name of the search parameter ("*" passes all form fields)',
        'result_name': 'Name of the result list returned by the controller',
        'only_suggest': 'If true, pressing enter does not automatically submit the first list item.',
        'complete_delay': 'Delay (in seconds) before loading new auto completions',
        'take_focus': 'If true, take focus on load.',
        'min_chars': 'Minimum number of characters to type before autocomplete activates',
        'show_spinner': 'If false, the spinner (load indicator) is not shown.'
    }
    attrs = {}
    search_controller = ''
    search_param = 'searchString'
    result_name = 'textItems'
    only_suggest = False
    complete_delay = 0.200
    take_focus = False
    min_chars = 1
    show_spinner = True


class AutoCompleteField(CompoundFormField, AutoComplete):
    """Text field with auto complete functionality and hidden key field."""

    template = """
    <span xmlns:py="http://genshi.edgewall.org/" id="${field_id}" class="${field_class}">
    <script type="text/javascript">
        AutoCompleteManager${field_id} = new AutoCompleteManager('${field_id}',
        '${text_field.field_id}', '${hidden_field.field_id}',
        '${search_controller}', '${search_param}', '${result_name}',${str(only_suggest).lower()},
        '${show_spinner and tg.url([tg.widgets, 'turbogears.widgets/spinner.gif']) or None}',
        ${complete_delay}, ${str(take_focus).lower()}, ${min_chars});
        addLoadEvent(AutoCompleteManager${field_id}.initialize);
    </script>
    ${text_field.display(value_for(text_field), **params_for(text_field))}
    <img py:if="show_spinner" id="autoCompleteSpinner${field_id}"
        src="${tg.url([tg.widgets, 'turbogears.widgets/spinnerstopped.png'])}" alt=""/>
    <span class="autoTextResults" id="autoCompleteResults${field_id}"/>
    ${hidden_field.display(value_for(hidden_field), **params_for(hidden_field))}
    </span>
    """
    member_widgets = ['text_field', 'hidden_field']
    text_field = TextField(name='text')
    hidden_field = HiddenField(name='hidden')


class AutoCompleteFieldDesc(CoreWD):

    name = "AutoCompleteField"
    codes = """AK AL AR AS AZ CA CO CT DC DE FL FM GA GU HI IA ID IL IN KS
        KY LA MA MD ME MH MI MN MO MP MS MT NC ND NE NH NJ NM NV NY OH
        OK OR PA PR PW RI SC SD TN TX UM UT VA VI VT WA WI WV WY""".split()
    states = """Alaska Alabama Arkansas American_Samoa Arizona
        California Colorado Connecticut District_of_Columbia
        Delaware Florida Federated_States_of_Micronesia Georgia Guam
        Hawaii Iowa Idaho Illinois Indiana Kansas Kentucky Louisiana
        Massachusetts Maryland Maine Marshall_Islands Michigan
        Minnesota Missouri Northern_Mariana_Islands Mississippi
        Montana North_Carolina North_Dakota Nebraska New_Hampshire
        New_Jersey New_Mexico Nevada New_York Ohio Oklahoma Oregon
        Pennsylvania Puerto_Rico Palau Rhode_Island South_Carolina
        South_Dakota Tennessee Texas U.S._Minor_Outlying_Islands
        Utah Virginia Virgin_Islands_of_the_U.S. Vermont Washington
        Wisconsin West_Virginia Wyoming""".split()
    states = map(lambda s: s.replace('_', ' '), states)
    state_code = dict(zip(codes, states))
    template = """
    <form xmlns:py="http://genshi.edgewall.org/" onsubmit="if (
        this.elements[0].value &amp;&amp; this.elements[1].value)
        alert('The alpha code for '+this.elements[0].value
        +' is '+this.elements[1].value+'.');return false"><table>
        <tr><th>State</th><td py:content="for_widget.display()"/>
        <td><input type="submit" value="Show alpha code"/></td></tr>
    </table></form>
    """
    full_class_name = "turbogears.widgets.AutoCompleteField"

    def __init__(self, *args, **kw):
        super(AutoCompleteFieldDesc, self).__init__(*args, **kw)
        self.for_widget = AutoCompleteField(name='state_and_code',
            search_controller='%s/search' % self.full_class_name,
            search_param='state', result_name='states')

    @expose('json')
    def search(self, state):
        states = []
        code = state.upper()
        if code in self.state_code:
            states.append((self.state_code[code], code))
        else:
            states.extend([s for s  in zip(self.states, self.codes)
                if s[0].lower().startswith(state.lower())])
        return dict(states=states)


class AutoCompleteTextField(TextField, AutoComplete):
    """Text field with auto complete functionality."""

    template = """
    <span xmlns:py="http://genshi.edgewall.org/" class="${field_class}">
    <script type="text/javascript">
        AutoCompleteManager${field_id} = new AutoCompleteManager('${field_id}', '${field_id}', null,
        '${search_controller}', '${search_param}', '${result_name}', ${str(only_suggest).lower()},
        '${show_spinner and tg.url([tg.widgets, 'turbogears.widgets/spinner.gif']) or None}',
        ${complete_delay}, ${str(take_focus).lower()}, ${min_chars});
        addLoadEvent(AutoCompleteManager${field_id}.initialize);
    </script>
    <input type="text" name="${name}" class="${field_class}" id="${field_id}"
        value="${value}" py:attrs="attrs"/>
    <img py:if="show_spinner" id="autoCompleteSpinner${field_id}"
        src="${tg.url([tg.widgets, 'turbogears.widgets/spinnerstopped.png'])}" alt=""/>
    <span class="autoTextResults" id="autoCompleteResults${field_id}"/>
    </span>
    """


class AutoCompleteTextFieldDesc(CoreWD):

    name = "AutoCompleteTextField"
    states = AutoCompleteFieldDesc.states
    state_code = AutoCompleteFieldDesc.state_code
    template = """
    <table xmlns:py="http://genshi.edgewall.org/">
        <tr><th>State</th><td py:content="for_widget.display()"/></tr>
    </table>
    """
    full_class_name = "turbogears.widgets.AutoCompleteTextField"

    def __init__(self, *args, **kw):
        super(AutoCompleteTextFieldDesc, self).__init__(*args, **kw)
        self.for_widget = AutoCompleteTextField(name="state_only",
            search_controller='%s/search' % self.full_class_name,
            search_param='state', result_name='states')

    @expose('json')
    def search(self, state):
        states = []
        code = state.upper()
        if code in self.state_code:
            states.append(self.state_code[code])
        else:
            states.extend([s for s  in self.states
                if s.lower().startswith(state.lower())])
        return dict(states=states)


class LinkRemoteFunction(RPC):
    """Link with remote execution.

    Returns a link that executes a POST asynchronously
    and updates a DOM Object with the result of it.

    """

    template = """
    <a xmlns:py="http://genshi.edgewall.org/" name="${name}"
        py:attrs="attrs" py:content="value" onclick="${js}" href="#"/>
    """

    params = ['attrs']
    attrs = {}


class LinkRemoteFunctionDesc(CoreWD):

    name = "AJAX remote function"
    states = AutoCompleteFieldDesc.states
    template = """
    <div id="items">
        ${for_widget.display("States starting with the letter 'N'", update="items")}
    </div>
    """
    full_class_name = 'turbogears.widgets.LinkRemoteFunction'

    def __init__(self, *args, **kw):
        super(LinkRemoteFunctionDesc, self).__init__(*args, **kw)
        self.for_widget = LinkRemoteFunction(
            name='linkrf', action='%s/search_linkrf' % self.full_class_name,
            data=dict(state_starts_with='N'))

    @expose()
    def search_linkrf(self, state_starts_with):
        return '<br/>'.join(
            [s for s in self.states if s.startswith(state_starts_with)])


class RemoteForm(RPC, TableForm):
    """AJAX table form.

    A TableForm that submits the data asynchronously and loads the resulting
    HTML into a DOM object

    """

    def update_params(self, d):
        super(RemoteForm, self).update_params(d)
        d['form_attrs']['onSubmit'] = "return !remoteFormRequest(this, '%s', %s);" % (
            d.get('update', ''), jsonify.encode(self.get_options(d)))


class RemoteFormDesc(CoreWD):

    name = "AJAX Form"
    template = """
    <div>
        ${for_widget.display()}
        <div id="post_data">&nbsp;</div>
    </div>
    """
    full_class_name = 'turbogears.widgets.RemoteForm'

    class TestFormFields(WidgetsList):
        name = TextField()
        age = TextField()
        check = CheckBox()
        radio = RadioButtonList(options=list(enumerate(
            "Python Java Pascal Ruby".split())), default=3)

    def __init__(self, *args, **kw):
        super(RemoteFormDesc, self).__init__(*args, **kw)
        self.for_widget = RemoteForm(
            fields=self.TestFormFields(),
            name='remote_form',
            update='post_data',
            action='%s/post_data_rf' % self.full_class_name,
            before="alert('pre-hook')",
            confirm="Confirm?",
        )

    @expose()
    def post_data_rf(self, **kw):
        return """Received data:<br/>%r""" % kw


ajaxgridcounter = itertools.count()

class AjaxGrid(Widget):
    """AJAX updateable datagrid based on widget.js grid"""

    template = """<div id="${id}" xmlns:py="http://genshi.edgewall.org/">
    <a py:if="refresh_text"
       href="#"
       onclick="javascript:${id}_AjaxGrid.refresh(${defaults});return false;">
       ${refresh_text}
    </a>
    <div id="${id}_update"></div>
    <script type="text/javascript">
        addLoadEvent(partial(${id}_AjaxGrid.refresh, ${defaults}));
    </script>
    </div>
    """
    params = ['refresh_text', 'id', 'defaults']
    defaults = {}
    refresh_text = "Update"
    id = 'ajaxgrid_%d' % ajaxgridcounter.next()

    def __init__(self, refresh_url, *args, **kw):
        super(AjaxGrid, self).__init__(*args, **kw)
        target = '%s_update' % self.id
        self.javascript = [
            mochikit,
            JSLink('turbogears', 'js/widget.js'),
            JSLink(static, 'ajaxgrid.js'),
            JSSource("""
                %(id)s_AjaxGrid = new AjaxGrid('%(refresh_url)s', '%(target)s');
            """ % dict(id=self.id, refresh_url=refresh_url, target=target)
            ),
        ]

    def update_params(self, d):
        super(AjaxGrid, self).update_params(d)
        d['defaults'] = jsonify.encode(d['defaults'])


class AjaxGridDesc(CoreWD):

    name = "AJAX Grid"
    full_class_name = 'turbogears.widgets.AjaxGrid'

    @staticmethod
    def facgen(n):
        total = 1
        yield 0, 1
        for k in xrange(1, n+1):
            total *= k
            yield k, total


    def __init__(self, *args, **kw):
        super(AjaxGridDesc, self).__init__(*args, **kw)
        self.for_widget = AjaxGrid(
            refresh_url = "%s/update" % self.full_class_name,
            # Dummy default params, just POC
            defaults = dict(),
        )
        self.update_count = itertools.count()

    @expose('json')
    def update(self):
        return dict(
            headers = ['N', 'fact(N)'],
            rows = list(self.facgen(self.update_count.next())),
        )


class URLLink(FormField):
    """Hyperlink"""

    template = """
    <a xmlns:py="http://genshi.edgewall.org/"
       href="$link"
       target="$target"
       py:attrs="attrs"
    >$text</a>
    """
    params = ['target', 'text', 'link', 'attrs']
    attrs = {}
    params_doc = {'link': 'Hyperlink',
                  'target': 'Specify where the link should be opened',
                  'text': 'The message to be shown for the link',
                  'attrs': 'Extra attributes'}
