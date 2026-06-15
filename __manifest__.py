{
    'name': 'Календар Подій',
    'version': '19.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Єдиний календар подій, CRM-угод та записів з локаціями для LEM Station',
    'description': """
Календар Подій — LEM Station
==============================

Єдиний календар для управління подіями, CRM-угодами та ручними записами.

Можливості:
-----------
* **Єдиний календар** — події, CRM-угоди та ручні записи в одному місці
* **Локації** — прив'язка до локацій з кольоровим маркуванням
* **Статуси** — В процесі погодження, Погоджено, Резерв, Очікуємо відповідь, Скасовано
* **Фільтри** — по локації, типу запису та статусу в sidebar
* **Chatter** — повний лог змін через mail.thread
    """,
    'author': 'LEM Station',
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
            'lem_event_calendar/static/src/lem_object_link.js',
            'lem_event_calendar/static/src/views/lem_event_calendar/lem_event_calendar_model.js',
            'lem_event_calendar/static/src/views/lem_event_calendar/lem_event_calendar_filter_section_patch.js',
            'lem_event_calendar/static/src/views/lem_event_calendar/lem_event_calendar_common_renderer.js',
            'lem_event_calendar/static/src/views/lem_event_calendar/lem_event_calendar_renderer.js',
            'lem_event_calendar/static/src/views/lem_event_calendar/lem_event_calendar_view.js',
        ],
    },
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}
