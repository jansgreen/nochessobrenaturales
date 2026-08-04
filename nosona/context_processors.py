from django.conf import settings


OPEN_GRAPH_LOCALES = {
    'es': 'es_ES',
    'en': 'en_US',
    'pt': 'pt_PT',
}


def language_navigation(request):
    current_language = getattr(
        request,
        'LANGUAGE_CODE',
        settings.LANGUAGE_CODE,
    ).split('-', 1)[0]
    languages = []
    for code, name in settings.LANGUAGES:
        languages.append(
            {
                'code': code,
                'name': str(name),
                'is_active': code == current_language,
            }
        )

    return {
        'active_language': current_language,
        'language_options': languages,
        'open_graph_locale': OPEN_GRAPH_LOCALES.get(
            current_language,
            OPEN_GRAPH_LOCALES['es'],
        ),
    }
