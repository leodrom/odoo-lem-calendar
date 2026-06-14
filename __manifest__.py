{
    'name': 'Календар Подій',
    'version': '19.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Unified calendar: events, opportunities and standalone entries with locations',
    'depends': ['mail', 'event', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/lem_location_views.xml',
        'views/lem_event_calendar_entry_views.xml',
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'lem_event_calendar/static/src/css/calendar.css',
            'lem_event_calendar/static/src/views/lem_event_calendar/lem_event_calendar_model.js',
            'lem_event_calendar/static/src/views/lem_event_calendar/lem_event_calendar_common_renderer.js',
            'lem_event_calendar/static/src/views/lem_event_calendar/lem_event_calendar_renderer.js',
            'lem_event_calendar/static/src/views/lem_event_calendar/lem_event_calendar_view.js',
        ],
    },
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}
