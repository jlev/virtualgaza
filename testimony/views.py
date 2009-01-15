from django.http import Http404
from testimony.models import Text

def diaryDetail(request, id):
    try:
        d = Text.objects.get(pk=id)
    except Text.DoesNotExist:
        raise Http404
    return render_to_response('testimony/diary.html', {'text': d})