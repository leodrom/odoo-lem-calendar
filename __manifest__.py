{
    'name': 'Календар Подій',
    'version': '19.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Unified calendar: events, opportunities and standalone entries with locations',
    'depends': ['mail', 'event', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/lem_location_views.xml',
        'views/lem_calendar_entry_views.xml',
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'lem_calendar/static/src/css/calendar.css',
            'lem_calendar/static/src/views/lem_calendar/lem_calendar_common_renderer.js',
            'lem_calendar/static/src/views/lem_calendar/lem_calendar_renderer.js',
            'lem_calendar/static/src/views/lem_calendar/lem_calendar_view.js',
        ],
    },
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}
