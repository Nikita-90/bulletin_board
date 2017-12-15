from __future__ import unicode_literals

from bulletin_board.celery import app

import bulletin_board_app.models


@app.task(bind=True)
def deactivate_advert(self, advert_pk, task_id):
    print '\nCELERY WORK'
    try:
        advert = bulletin_board_app.models.Advert.objects.get(pk=advert_pk, task=task_id)
        advert.is_active = False
        advert.save()
    except:
        pass